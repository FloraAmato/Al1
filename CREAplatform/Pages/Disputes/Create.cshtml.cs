using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using CreaProject.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace CreaProject.Pages.Disputes
{
    #region snippetCtor

    public class CreateModel : DisputeBasePageModel
    {
        public IActionResult OnGet()
        {
            return Page();
        }

        #region snippet_Create

        public async Task<IActionResult> OnPostAsync()
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

        #endregion

        public CreateModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        #endregion
    }
}