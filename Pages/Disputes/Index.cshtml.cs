using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using CreaProject.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Localization;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CreaProject.Helpers;

namespace CreaProject.Pages.Disputes
{
    public class IndexModel : DisputeBasePageModel
    {
        public IndexModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager,
            IStringLocalizer<DisputeBasePageModel> localizer
        )
            : base(context, authorizationService, userManager, localizer)
        {
        }

        public IList<Dispute> MyDisputes { get; set; }
        
        public string CurrentUserId { get; set; }
        
        [BindProperty]
        public int DeleteDisputeId { get; set; }

        public async Task OnGetAsync()
        {
            List<Dispute> disputes = await Context
                .Disputes.Include(d => d.Goods)
                .Include(d => d.Agents)
                .ThenInclude(a => a.CreaUser)
                .AsNoTracking()
                .ToListAsync();

            bool isAuthorized =
                User.IsInRole(Constants.DisputeManagersRole)
                || User.IsInRole(Constants.ContactAdministratorsRole);

            CurrentUserId = UserManager.GetUserId(User);

            if (!isAuthorized)
            {
                HashSet<int> currentUserDisputes =
                    [..Context.Agents.Where(d => d.CreaUserId == CurrentUserId).Select(d => d.DisputeId)];
                MyDisputes = disputes.Where(c => c.OwnerId == CurrentUserId || currentUserDisputes.Contains(c.DisputeId)).ToList();
            }

            ViewData["CurrentUserId"] = CurrentUserId;
        }

        public async Task<IActionResult> OnPostCreateDisputeAsync()
        {
            if (!ModelState.IsValid)
                return RedirectToPage("Index");

            Dispute.OwnerId = UserManager.GetUserId(User);
            Dispute.Status = DisputeStatus.SettingUp;
            Dispute.ResolutionMethod = DisputeResolutionMethod.Ratings;
            Dispute.RatingWeight = 10;
            Dispute.BoundsPercentage = 25;

            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                Dispute,
                DisputeOperations.Create
            );
            if (!isAuthorized.Succeeded)
                return new ChallengeResult();

            Context.Disputes.Add(Dispute);
            
            await Context.SaveChangesAsync();

            CreaUser creator = await UserManager.GetUserAsync(User);

            if (creator == null) return NotFound();

            Agent agent = new()
            {
                DisputeId = Dispute.DisputeId,
                Email = creator.Email,
                CreaUserId = creator.Id,
                CreaUser = creator
            };

            Context.Attach(creator);

            Context.Agents.Add(agent);
            
            await Context.SaveChangesAsync();

            int newDisputeId = Dispute.DisputeId;

            return Redirect($"./Disputes/Create/{newDisputeId}");
        }

        public async Task<IActionResult> OnPostDeleteDisputeAsync()
        {
            Dispute disputeToDelete = await Context.Disputes.FindAsync(DeleteDisputeId);

            if (disputeToDelete == null) return NotFound();

            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                disputeToDelete,
                DisputeOperations.Delete
            );
            if (!isAuthorized.Succeeded)
                return new ChallengeResult();

            Context.Disputes.Remove(disputeToDelete);
            await Context.SaveChangesAsync();

            return RedirectToPage("./Index");
        }
    }
}
