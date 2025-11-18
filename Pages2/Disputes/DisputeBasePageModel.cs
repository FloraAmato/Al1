using System.Collections.Generic;
using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Data;
using CreaProject.Helpers;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Localization;

namespace CreaProject.Pages.Disputes
{
    public class DisputeBasePageModel : PageModel
    {
        private readonly IStringLocalizer<DisputeBasePageModel> _localizer;
        private MailjetService _mailjetService;

        public DisputeBasePageModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager,
            IStringLocalizer<DisputeBasePageModel> localizer
        )
        {
            Context = context;
            UserManager = userManager;
            AuthorizationService = authorizationService;
            _localizer = localizer;
        }

        public IStringLocalizer<DisputeBasePageModel> Localizer => _localizer;
        protected ApplicationDbContext Context { get; }
        protected IAuthorizationService AuthorizationService { get; }
        protected UserManager<CreaUser> UserManager { get; }
        
        [BindProperty]
        public Dispute Dispute { get; set; }
        
    }
}
