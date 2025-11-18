using CreaProject.Areas.Identity.Data;
using CreaProject.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CreaProject.Pages.Disputes
{
    public class DisputeBasePageModel : PageModel
    {
        public DisputeBasePageModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
        {
            Context = context;
            UserManager = userManager;
            AuthorizationService = authorizationService;
        }

        protected ApplicationDbContext Context { get; }
        protected IAuthorizationService AuthorizationService { get; }
        protected UserManager<CreaUser> UserManager { get; }


        [BindProperty] public Dispute Dispute { get; set; }
    }
}