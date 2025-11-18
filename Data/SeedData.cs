using System;
using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace CreaProject.Data
{
    public static class SeedData
    {
        public static async Task Initialize(IServiceProvider serviceProvider, string testUserPw)
        {
            using (
                var context = new ApplicationDbContext(
                    serviceProvider.GetRequiredService<DbContextOptions<ApplicationDbContext>>()
                )
            )
            {
                // For sample purposes seed both with the same password.
                // Password is set with the following:
                // dotnet user-secrets set SeedUserPW <pw>
                // The admin user can do anything

                var adminId = await EnsureUser(serviceProvider, testUserPw, "admin@crea.eu");
                await EnsureRole(serviceProvider, adminId, Constants.ContactAdministratorsRole);

                // allowed user can create and edit contacts that they create
                var managerId = await EnsureUser(serviceProvider, testUserPw, "manager@crea.eu");
                await EnsureRole(serviceProvider, managerId, Constants.DisputeManagersRole);

                SeedDb(context, adminId);
            }
        }

        private static async Task<string> EnsureUser(
            IServiceProvider serviceProvider,
            string testUserPw,
            string userName
        )
        {
            var userManager = serviceProvider.GetService<UserManager<CreaUser>>();

            var user = await userManager.FindByNameAsync(userName);
            if (user == null)
            {
                user = new CreaUser { UserName = userName, EmailConfirmed = true };
                await userManager.CreateAsync(user, testUserPw);
            }

            if (user == null)
                throw new Exception("The password is probably not strong enough!");

            return user.Id;
        }

        private static async Task<IdentityResult> EnsureRole(
            IServiceProvider serviceProvider,
            string uid,
            string role
        )
        {
            IdentityResult ir = null;
            var roleManager = serviceProvider.GetService<RoleManager<IdentityRole>>();

            if (roleManager == null)
                throw new Exception("roleManager null");

            if (!await roleManager.RoleExistsAsync(role))
                ir = await roleManager.CreateAsync(new IdentityRole(role));

            var userManager = serviceProvider.GetService<UserManager<CreaUser>>();

            var user = await userManager.FindByIdAsync(uid);

            if (user == null)
                throw new Exception("The testUserPw password was probably not strong enough!");

            ir = await userManager.AddToRoleAsync(user, role);

            return ir;
        }

        public static void SeedDb(ApplicationDbContext context, string adminId) { }
    }
}
