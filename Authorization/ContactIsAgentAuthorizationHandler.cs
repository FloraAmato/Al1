using System.Linq;
using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace CreaProject.Authorization
{
    public class ContactIsAgentAuthorizationHandler
        : AuthorizationHandler<OperationAuthorizationRequirement, Dispute>
    {
        private readonly ApplicationDbContext _context;
        private readonly UserManager<CreaUser> _userManager;

        public ContactIsAgentAuthorizationHandler(
            UserManager<CreaUser> userManager,
            ApplicationDbContext context
        )
        {
            _userManager = userManager;
            _context = context;
        }

        protected override Task HandleRequirementAsync(
            AuthorizationHandlerContext context,
            OperationAuthorizationRequirement requirement,
            Dispute dispute
        )
        {
            if (context.User == null || dispute == null)
                return Task.CompletedTask;

            // If not asking for CRUD permission, return.

            if (requirement.Name != Constants.BidOperationName  && requirement.Name != Constants.UpdateOperationName)
                return Task.CompletedTask;

            var agents = _context
                .Disputes.Include(d => d.Agents)
                .Where(d => d.DisputeId == dispute.DisputeId)
                .AsNoTracking()
                .FirstOrDefault()
                .Agents;

            if (agents.Exists(a => a.CreaUserId == _userManager.GetUserId(context.User)))
                context.Succeed(requirement);

            return Task.CompletedTask;
        }
    }
}
