using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;
using Microsoft.AspNetCore.Identity;

namespace CreaProject.Authorization
{
    public class ContactIsOwnerAuthorizationHandler
        : AuthorizationHandler<OperationAuthorizationRequirement, Dispute>
    {
        private readonly UserManager<CreaUser> _userManager;

        public ContactIsOwnerAuthorizationHandler(UserManager<CreaUser> userManager)
        {
            _userManager = userManager;
        }

        protected override Task HandleRequirementAsync(
            AuthorizationHandlerContext context,
            OperationAuthorizationRequirement requirement,
            Dispute resource
        )
        {
            if (context.User == null || resource == null)
                return Task.CompletedTask;

            // If not asking for CRUD permission, return.

            if (
                requirement.Name != Constants.CreateOperationName
                && requirement.Name != Constants.ReadOperationName
                && requirement.Name != Constants.UpdateOperationName
                && requirement.Name != Constants.DeleteOperationName
            )
                return Task.CompletedTask;

            if (resource.OwnerId == _userManager.GetUserId(context.User))
                context.Succeed(requirement);

            return Task.CompletedTask;
        }
    }
}
