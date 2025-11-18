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

    public class EditRatesModel : DisputeBasePageModel
    {
        public EditRatesModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        [BindProperty] public List<Rate> AgentRates { get; set; }


        public async Task<IActionResult> OnGetAsync(int id)
        {
            Dispute = await Context.Disputes
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities).ThenInclude(b => b.Good)
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
                var agentRates = Dispute.AgentUtilities.Cast<Rate>().Where(b => b.AgentId == agentId).ToList();

                AgentRates = agentRates.Count > 0 ? agentRates : new List<Rate>();

                var excludedIDs = new HashSet<int>(agentRates.Select(p => p.GoodId));
                var result = Dispute.Goods.Where(p => !excludedIDs.Contains(p.GoodId));

                foreach (var good in result)
                {
                    var rate = new Rate
                    {
                        Id = 0,
                        AgentId = agentId,
                        DisputeId = Dispute.DisputeId,
                        GoodId = good.GoodId,
                        Good = good,
                    };
                    AgentRates.Add(rate);
                }


                return Page();
            }

            if (User.Identity.IsAuthenticated)
                return new ForbidResult();
            return new ChallengeResult();
        }

        public async Task<IActionResult> OnPostSaveRatesAsync(int id)
        {


            // Fetch Dispute from DB to get OwnerID.
            Dispute = await Context
                .Disputes.Include(d => d.Goods).AsNoTracking()
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
                foreach (var rate in AgentRates)
                    if (rate.Id == 0)
                        Context.Rates.Add(rate);
                    else
                        Context.Attach(rate).State = EntityState.Modified;
                await Context.SaveChangesAsync();
            }
            catch (DbUpdateException)
            {
                return RedirectToPage("EditRates", new {id});
            }


            return RedirectToPage("EditRates", new {id});
        }
    }

    #endregion
}