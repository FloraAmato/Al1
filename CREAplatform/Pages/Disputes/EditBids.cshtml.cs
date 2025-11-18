using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using CreaProject.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CreaProject.Pages.Disputes
{
    #region snippet

    public class EditBidsModel : DisputeBasePageModel
    {
        public EditBidsModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        [BindProperty] public List<Bid> AgentBids { get; set; }


        public async Task<IActionResult> OnGetAsync(int id)
        {
            Dispute = await Context.Disputes.Include(d => d.Goods).Include(d => d.AgentUtilities)
                .ThenInclude(b => b.Good)
                .AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null) return NotFound();

            if (!(Dispute.Status.Equals(DisputeStatus.Bidding) | Dispute.Status.Equals(DisputeStatus.Finalizing)))
                return Unauthorized();


            var isAuthorized = await AuthorizationService.AuthorizeAsync(User, Dispute,
                DisputeOperations.Bid);

            if (isAuthorized.Succeeded)
            {
                var agentId = (await Context.Agents.Where(a => a.DisputeId == id && a.CreaUser.Id == UserManager.GetUserId(User))
                    .FirstOrDefaultAsync()).AgentId;
                var agentBids = Dispute.AgentUtilities.Cast<Bid>().Where(b => b.AgentId == agentId).ToList();
                var budget = Dispute.Goods.Sum(g => g.EstimatedValue);


                if (agentBids.Count > 0)
                    AgentBids = agentBids;
                else
                    AgentBids = new List<Bid>();

                var excludedIDs = new HashSet<int>(agentBids.Select(p => p.GoodId));
                var result = Dispute.Goods.Where(p => !excludedIDs.Contains(p.GoodId));

                foreach (var good in result)
                {
                    var bid = new Bid
                    {
                        Id = 0,
                        AgentId = agentId,
                        DisputeId = Dispute.DisputeId,
                        GoodId = good.GoodId,
                        Good = good, 
                        Dispute = Dispute
                    };
                    AgentBids.Add(bid);
                }


                ViewData["Budget"] = budget;

                return Page();
            }

            if (User.Identity.IsAuthenticated)
                return new ForbidResult();
            return new ChallengeResult();
        }

        public async Task<IActionResult> OnPostSaveBidsAsync(int id)
        {
            // Fetch Dispute from DB to get OwnerID.
            Dispute = await Context
                .Disputes
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                //.AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null) return NotFound();

            if (!Dispute.Status.Equals(DisputeStatus.Bidding))
                return Unauthorized();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, Dispute,
                DisputeOperations.Bid);
            if (!isAuthorized.Succeeded) return new ChallengeResult();

            try
            {
                var budget = Dispute.Goods.Sum(g => g.EstimatedValue);


                if (AgentBids.Sum(b => b.BidValue) == budget)
                {
                    var error = false;
                    foreach (var bid in AgentBids)
                    {
                        bid.Dispute = Dispute;
                        bid.Good = Context.Goods.Find(bid.GoodId);
                        if (!(bid.BidValue >= bid.LowerBound && bid.BidValue <= bid.UpperBound))
                        //if (bid.BidValue >= bid.LowerBound)
                        {
                            var goodName = Context.Goods.Find(bid.GoodId).Name;
                            TempData["BidError"] = goodName;
                            TempData["LowerBound"] = $"{bid.LowerBound:C}";
                            TempData["UpperBound"] = $"{bid.UpperBound:C}";
                            error = true;
                            break;
                        }
                    }

                    if (!error)
                    {
                        foreach (var bid in AgentBids)
                        {
                            if (bid.Id == 0)
                                Dispute.AgentUtilities.Add(bid);
                            else
                                ((Bid)Dispute.AgentUtilities.First(u => u.Id == bid.Id)).BidValue = bid.BidValue;
                        }
                        await Context.SaveChangesAsync();
                    }

                }
                else
                {
                    TempData["BudgetError"] = true;
                    return RedirectToPage("EditBids", new {id});
                }
            }
            catch (DbUpdateException)
            {
                return RedirectToPage("EditBids", new {id});
            }


            return RedirectToPage("EditBids", new {id});
        }
    }

    #endregion
}