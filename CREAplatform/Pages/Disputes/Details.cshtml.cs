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

    public class DetailsModel : DisputeBasePageModel
    {
        public DetailsModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        public async Task<IActionResult> OnGetAsync(int id)
        {
            Dispute = await Context.Disputes.FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null) return NotFound();

            var isAuthorized = User.IsInRole(Constants.DisputeManagersRole) ||
                               User.IsInRole(Constants.ContactAdministratorsRole);

            var currentUserId = UserManager.GetUserId(User);

            if (!isAuthorized
                && currentUserId != Dispute.OwnerId
                && Dispute.Status != DisputeStatus.Finalizing)
                return new ChallengeResult();

            return Page();
        }

        public async Task<IActionResult> OnPostAsync(int id, DisputeStatus status)
        {
            var contact = await Context.Disputes.FirstOrDefaultAsync(
                m => m.DisputeId == id);

            if (contact == null) return NotFound();

            var contactOperation = status == DisputeStatus.Finalizing
                ? DisputeOperations.Approve
                : DisputeOperations.Reject;

            var isAuthorized = await AuthorizationService.AuthorizeAsync(User, contact,
                contactOperation);
            if (!isAuthorized.Succeeded) return new ChallengeResult();
            contact.Status = status;
            Context.Disputes.Update(contact);
            await Context.SaveChangesAsync();

            return RedirectToPage("./Index");
        }
    }

    #endregion
}