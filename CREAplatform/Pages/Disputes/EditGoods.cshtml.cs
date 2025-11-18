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

    public class EditGoodsModel : DisputeBasePageModel
    {
        public EditGoodsModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        [BindProperty] public Good NewGood { get; set; }

        [BindProperty] public int RemoveGoodId { get; set; }

        public async Task<IActionResult> OnGetAsync(int id)
        {
            Dispute = await Context.Disputes
                .Include(m => m.Goods)
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

            return Page();
        }

        public async Task<IActionResult> OnPostAddGoodAsync(int id)
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

            NewGood.DisputeId = id;

            try
            {
                Context.Goods.Add(NewGood);
                await Context.SaveChangesAsync();
            }
            catch (DbUpdateException)
            {
                return RedirectToPage("EditGoods", new {id});
            }

            return RedirectToPage("EditGoods", new {id});
        }

        public async Task<IActionResult> OnPostRemoveGoodAsync()
        {
            var id = Dispute.DisputeId;

            // Fetch Dispute from DB to get OwnerID.
            var dispute = await Context
                .Disputes.AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (dispute == null) return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, dispute,
                DisputeOperations.Update);
            if (!isAuthorized.Succeeded) return new ChallengeResult();

            var good = await Context
                .Goods.AsNoTracking()
                .FirstOrDefaultAsync(m => m.GoodId == RemoveGoodId);


            if (good == null) return NotFound();


            Context.Goods.Remove(good);
            await Context.SaveChangesAsync();

            return RedirectToPage("EditGoods", new {id});
        }
    }

    #endregion
}