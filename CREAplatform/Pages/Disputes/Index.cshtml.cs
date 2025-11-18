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

    public class IndexModel : DisputeBasePageModel
    {
        public IndexModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        public IList<Dispute> MyDisputes { get; set; }
        public IList<Dispute> AgentDisputes { get; set; }

        [BindProperty] public int RemoveDisputeId { get; set; }

        public async Task OnGetAsync()
        {
            var disputes = await Context.Disputes.Include(d => d.Goods)
                .Include(d => d.Agents).ThenInclude(a => a.CreaUser)
                .AsNoTracking()
                .ToListAsync();

            var isAuthorized = User.IsInRole(Constants.DisputeManagersRole) ||
                               User.IsInRole(Constants.ContactAdministratorsRole);

            var currentUserId = UserManager.GetUserId(User);

            // Only approved disputes are shown UNLESS you're authorized to see them
            // or you are the owner.
            if (!isAuthorized)
            {
                var currentUserDisputes = Context.Agents.Where(d => d.CreaUserId == currentUserId)
                    .Select(d => d.DisputeId).ToList();
                MyDisputes = disputes.Where(c => c.OwnerId == currentUserId).ToList();
                AgentDisputes = disputes.Where(c =>
                    (c.Status == DisputeStatus.Bidding | c.Status== DisputeStatus.Finalizing) && currentUserDisputes.Contains(c.DisputeId)).ToList();
            }

            ViewData["CurrentUserId"] = currentUserId;
        }


        public async Task<IActionResult> OnPostCreateDisputeAsync()
        {
            if (!ModelState.IsValid) return RedirectToPage("Index");

            Dispute.OwnerId = UserManager.GetUserId(User);
            Dispute.Status = DisputeStatus.SettingUp;

            // requires using CreaProject.Authorization;
            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, Dispute,
                DisputeOperations.Create);
            if (!isAuthorized.Succeeded) return new ChallengeResult();

            Context.Disputes.Add(Dispute);
            await Context.SaveChangesAsync();

            return RedirectToPage("./Index");
        }


        public async Task<IActionResult> OnPostDeleteDisputeAsync()
        {
            var disputeId = RemoveDisputeId;

            Dispute = await Context.Disputes.FindAsync(disputeId);

            var contact = await Context
                .Disputes.AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == disputeId);

            if (contact == null) return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, contact,
                DisputeOperations.Delete);
            if (!isAuthorized.Succeeded) return new ChallengeResult();

            Context.Disputes.Remove(Dispute);
            await Context.SaveChangesAsync();

            return RedirectToPage("./Index");
        }
    }

    #endregion
}