using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using CreaProject.Data;
using CreaProject.Helpers;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Localization;

namespace CreaProject.Pages.Disputes
{
    public class Bids(
        ApplicationDbContext context,
        IAuthorizationService authorizationService,
        UserManager<CreaUser> userManager,
        IStringLocalizer<DisputeBasePageModel> localizer)
        : DisputeBasePageModel(context, authorizationService, userManager, localizer)
    {
        
        [BindProperty]
        public List<Bid> AgentBids { get; set; }
        
        [BindProperty]
        public List<Rate> AgentRates { get; set; }

        [BindProperty]
        public bool Validating { get; set; }

        public bool IsCurrentStep { get; set; } = false;

        public Agent CurrentAgent { get; set; }

        private async Task<Agent> GetCurrentAgent(int disputeId)
        {
            var agent = await Context
                    .Agents.Where(a =>
                        a.DisputeId == disputeId && a.CreaUser.Id == UserManager.GetUserId(User)
                    ).Include(a => a.CreaUser)
                    .FirstOrDefaultAsync();

            return agent;
        }
        
        public async Task<IActionResult> OnGetAsync(int disputeId)
        {
            Dispute = await Context.Disputes
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .ThenInclude(au => au.Agent)
                .Include(d => d.AgentUtilities)
                .ThenInclude(au => au.Good)
                .Include(d => d.Agents)
                .ThenInclude(a => a.CreaUser)
                .AsNoTracking()
                .FirstOrDefaultAsync(d => d.DisputeId == disputeId);
                
            if (Dispute == null) return NotFound();
            if (Dispute.Status == DisputeStatus.Bidding) IsCurrentStep = true;

            CurrentAgent = await this.GetCurrentAgent(disputeId);

            if (Dispute.ResolutionMethod == DisputeResolutionMethod.Bids)
            {
                AgentBids = Dispute
                    .AgentUtilities.Cast<Bid>()
                    .Where(b => b.AgentId == CurrentAgent.AgentId)
                    .ToList();
            }
            else
            {
                AgentRates = Dispute
                    .AgentUtilities.Cast<Rate>()
                    .Where(r => r.AgentId == CurrentAgent.AgentId)
                    .ToList();
            }

            var budget = Dispute.Goods.Sum(g => g.EstimatedValue);
            
            return Page();
        }

        public async Task<IActionResult> OnPostSaveBidsAsync(int disputeId)
        {
            Dispute = await Context.Disputes
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .Include(d => d.Agents)
                .FirstOrDefaultAsync(m => m.DisputeId == disputeId);

            if (Dispute == null) return NotFound();
            if (!Dispute.Status.Equals(DisputeStatus.Bidding)) return Unauthorized();
            
            Agent currentAgent = await this.GetCurrentAgent(Dispute.DisputeId);
            
            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                Dispute,
                DisputeOperations.Bid
            );
            if (!isAuthorized.Succeeded || currentAgent.Validated > ValidatedSteps.Bids) return new ChallengeResult();


            if (Dispute.ResolutionMethod == DisputeResolutionMethod.Bids)
            {
                decimal budget = Dispute.Goods.Sum(g => g.EstimatedValue);
                if (AgentBids.Sum(b => b.BidValue) != budget)
                {
                    TempData["BudgetError"] = true;
                    return RedirectToPage("Bids", new { disputeId });
                }
                
                foreach (Bid bid in AgentBids)
                {
                    Bid existingBid = await Context.Bids.FirstOrDefaultAsync(b => b.Id == bid.Id);
                    if (existingBid == null) return NotFound();
                    if (!(bid.BidValue >= existingBid.LowerBound && bid.BidValue <= existingBid.UpperBound))
                    {
                        TempData[""] = true;
                        return RedirectToPage("Bids", new { disputeId });
                    }
                
                    existingBid.BidValue = bid.BidValue;
                }
            }
            else
            {
                foreach (Rate rate in AgentRates)
                {
                    Rate existingRate = await Context.Rates.FirstOrDefaultAsync(r => r.Id == rate.Id);
                    if (existingRate == null) return NotFound();
                    existingRate.RateValue = rate.RateValue;
                }
            }

            await Context.SaveChangesAsync();
            if (Validating)
            {
                currentAgent.Validated = ValidatedSteps.Bids;
            }
            else
            {
                currentAgent.Validated = ValidatedSteps.Setup;
            }
            await Context.SaveChangesAsync();
            
            bool allAgentsValidated = Dispute.Agents.All(a => a.Validated == ValidatedSteps.Bids);
            if (!allAgentsValidated) return RedirectToPage("./Index");
            
            Dispute.Status = DisputeStatus.Finalizing;
            await Context.SaveChangesAsync();
            
            return Redirect($"/Disputes/Solution/{Dispute.DisputeId}");
        }
    }
}
