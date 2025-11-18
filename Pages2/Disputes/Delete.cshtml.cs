using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using CreaProject.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Localization;
using System.Threading.Tasks;
using CreaProject.Helpers;

namespace CreaProject.Pages.Disputes
{
    #region snippet

    public class DeleteModel : DisputeBasePageModel
    {
        public DeleteModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager,
            IStringLocalizer<DisputeBasePageModel> localizer
        )
            : base(context, authorizationService, userManager, localizer) { }

        public async Task<IActionResult> OnGetAsync(int id)
        {
            Dispute = await Context.Disputes.FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null)
                return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                Dispute,
                DisputeOperations.Delete
            );
            if (!isAuthorized.Succeeded)
                return new ChallengeResult();

            return Page();
        }

        public async Task<IActionResult> OnPostAsync(int id)
        {
            Dispute = await Context.Disputes.FindAsync(id);

            var contact = await Context
                .Disputes.AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (contact == null)
                return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                contact,
                DisputeOperations.Delete
            );
            if (!isAuthorized.Succeeded)
                return new ChallengeResult();

            Context.Disputes.Remove(Dispute);
            await Context.SaveChangesAsync();

            return RedirectToPage("./Index");
        }
    }

    #endregion
}
