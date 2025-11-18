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
    public class EditModel : DisputeBasePageModel
    {
        public EditModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        public async Task<IActionResult> OnGetAsync(int id)
        {
            Dispute = await Context.Disputes
                .Include(d => d.Agents)
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null) return NotFound();

            var isMediator = await AuthorizationService.AuthorizeAsync(User, Dispute,
                DisputeOperations.Update);
            var isAgent = await AuthorizationService.AuthorizeAsync(User, Dispute,
                DisputeOperations.Bid);

            if (!isMediator.Succeeded && !isAgent.Succeeded)
                return new ChallengeResult();

            if (isMediator.Succeeded)
                TempData["IsMediator"] = true;
            else
                TempData["IsMediator"] = false;

            var agentsCount = Dispute.Agents.Count;
            var goodsCount = Dispute.Goods.Count;
            ViewData["AgentsCount"] = agentsCount;
            ViewData["GoodsCount"] = goodsCount;

            if (isMediator.Succeeded && Dispute.Status == DisputeStatus.Bidding)
            {
                var agentsThatBidId = Dispute.AgentUtilities.Select(d => d.AgentId).Distinct().ToList();
                var agents = Dispute.Agents.Select(a => a.AgentId).ToList();
                var allBid = agentsThatBidId.All(agents.Contains) && agentsThatBidId.Count == agents.Count;
                ViewData["AllBid"] = allBid;
            }

            return Page();
        }

        public async Task<IActionResult> OnPostAsync(int id)
        {

            // Fetch Dispute from DB to get OwnerID.
            var dispute = await Context
                .Disputes.AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (dispute == null) return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, dispute,
                DisputeOperations.Update);
            if (!isAuthorized.Succeeded) return new ChallengeResult();


            Dispute.DisputeId = id;
            Dispute.OwnerId = dispute.OwnerId;

            if (Dispute.Name != null) dispute.Name = Dispute.Name;

            if (dispute.Status.Equals(DisputeStatus.SettingUp)) dispute.ResolutionMethod = Dispute.ResolutionMethod;

            Context.Attach(dispute).State = EntityState.Modified;
            await Context.SaveChangesAsync();

            return RedirectToPage("Edit", new {id});
        }


        public async Task<IActionResult> OnPostStartBiddingAsync(int id)
        {

            // Fetch Dispute from DB to get OwnerID.
            Dispute = await Context
                .Disputes.Include(d => d.Agents).Include(d => d.Goods).AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null) return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, Dispute,
                DisputeOperations.Update);
            if (!isAuthorized.Succeeded) return new ChallengeResult();

            if (Dispute.Agents.Count > 1 && Dispute.Goods.Count > 1 && Dispute.Status == DisputeStatus.SettingUp)
            {
                var shareSum = 0.0;
                foreach (var agent in Dispute.Agents)
                {
                    shareSum = shareSum + (double)agent.ShareOfEntitlement;
                } 
                if (shareSum<=100 && shareSum>99.9){
                    Dispute.Status = DisputeStatus.Bidding;
                    Context.Attach(Dispute).State = EntityState.Modified;
                    await Context.SaveChangesAsync();
                }
                else
                {
                    TempData["ErrorShareSum"] = "The sum of Share of entitlement is not equal to 100%";
                }
            }


            return RedirectToPage("Edit", new {id});
        }


        public async Task<IActionResult> OnPostStartEvaluationAsync(int id)
        {

            // Fetch Dispute from DB to get OwnerID.
            Dispute = await Context
                .Disputes
                .AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null) return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, Dispute,
                DisputeOperations.Update);
            if (!isAuthorized.Succeeded) return new ChallengeResult();

            Dispute.Status = DisputeStatus.Finalizing;
            Context.Attach(Dispute).State = EntityState.Modified;
            await Context.SaveChangesAsync();


            return RedirectToPage("Edit", new {id});
        }
    }
}