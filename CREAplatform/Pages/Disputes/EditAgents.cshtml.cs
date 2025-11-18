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

    public class EditAgentsModel : DisputeBasePageModel
    {
        public EditAgentsModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        [BindProperty] public Agent Agent { get; set; }

        [BindProperty] public int RemoveAgentId { get; set; }

        public async Task<IActionResult> OnGetAsync(int id)
        {
            Dispute = await Context.Disputes
                .Include(m => m.Agents)
                .ThenInclude(a => a.CreaUser)
                .AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null) return NotFound();

            var isMediator = await AuthorizationService.AuthorizeAsync(User, Dispute,
                DisputeOperations.Update);
            var isAgent = await AuthorizationService.AuthorizeAsync(User, Dispute,
                DisputeOperations.Bid);

            if (!isMediator.Succeeded && !isAgent.Succeeded)
                return new ChallengeResult();

            foreach (var agent in Dispute.Agents)
            {
                agent.Dispute = Dispute;
            }

            if (isMediator.Succeeded)
                TempData["IsMediator"] = true;
            else
                TempData["IsMediator"] = false;

            return Page();
        }

        public async Task<IActionResult> OnPostAddAgentAsync(int id)
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

            Agent.DisputeId = id;

            try
            {
                var user = await Context.Users.AsNoTracking()
                    .FirstOrDefaultAsync(m => m.Email == Agent.Email);

                if (user == null)
                {
                    //TODO: Invite user
                }
                else
                {
                    Agent.CreaUserId = user.Id;
                }

                Context.Agents.Add(Agent);
                await Context.SaveChangesAsync();
            }
            catch (DbUpdateException)
            {
                return RedirectToPage("EditAgents", new {id});
            }

            return RedirectToPage("EditAgents", new {id});
        }

        public async Task<IActionResult> OnPostRemoveAgentAsync()
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

            var agent = await Context
                .Agents.AsNoTracking()
                .FirstOrDefaultAsync(m => m.AgentId == RemoveAgentId);


            if (agent == null) return NotFound();


            Context.Agents.Remove(agent);
            await Context.SaveChangesAsync();

            return RedirectToPage("EditAgents", new {id});
        }
    }

    #endregion
}