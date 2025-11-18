using System.Threading.Tasks;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;

namespace CreaProject.Authorization
{
    public class ContactManagerAuthorizationHandler :
        AuthorizationHandler<OperationAuthorizationRequirement, Dispute>
    {
        protected override Task
            HandleRequirementAsync(AuthorizationHandlerContext context,
                OperationAuthorizationRequirement requirement,
                Dispute resource)
        {
            if (context.User == null || resource == null) return Task.CompletedTask;

            // If not asking for approval/reject, return.
            if (requirement.Name != Constants.ApproveOperationName &&
                requirement.Name != Constants.RejectOperationName)
                return Task.CompletedTask;

            // Managers can approve or reject.
            if (context.User.IsInRole(Constants.DisputeManagersRole)) context.Succeed(requirement);

            return Task.CompletedTask;
        }
    }
}