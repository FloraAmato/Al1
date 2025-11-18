using System.Threading.Tasks;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;

namespace CreaProject.Authorization
{
    public class ContactAdministratorsAuthorizationHandler
        : AuthorizationHandler<OperationAuthorizationRequirement, Dispute>
    {
        protected override Task HandleRequirementAsync(
            AuthorizationHandlerContext context,
            OperationAuthorizationRequirement requirement,
            Dispute resource)
        {
            if (context.User == null) return Task.CompletedTask;

            // Administrators can do anything.
            if (context.User.IsInRole(Constants.ContactAdministratorsRole)) context.Succeed(requirement);

            return Task.CompletedTask;
        }
    }
}