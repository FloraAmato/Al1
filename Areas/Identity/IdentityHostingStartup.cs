using System.Configuration;
using CreaProject.Areas.Identity;
using CreaProject.Areas.Identity.Data;
using CreaProject.Data;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Hosting;

[assembly: HostingStartup(typeof(IdentityHostingStartup))]

namespace CreaProject.Areas.Identity
{
    public class IdentityHostingStartup : IHostingStartup
    {
        public void Configure(IWebHostBuilder builder)
        {
            builder.ConfigureServices(
                (context, services) =>
                {
                    string connectionString = context.HostingEnvironment.IsDevelopment() 
                        ? context.Configuration["DatabaseUrlLocal"] 
                        : context.Configuration["DatabaseUrl"];
                    services.AddDbContext<ApplicationDbContext>(options =>
                        options.UseSqlServer(
                            connectionString
                        )
                    );

                    services
                        .AddIdentity<CreaUser, IdentityRole>(options => { })
                        .AddEntityFrameworkStores<ApplicationDbContext>()
                        .AddTokenProvider<DataProtectorTokenProvider<CreaUser>>(
                            TokenOptions.DefaultProvider
                        );

                    //services.AddDefaultIdentity<CreaUser>(options => options.SignIn.RequireConfirmedAccount = true)
                    //    .AddEntityFrameworkStores<ApplicationDbContext>();
                    services.TryAddScoped<UserManager<CreaUser>>();
                    services.TryAddScoped<RoleManager<IdentityRole>>();
                }
            );
        }
    }
}
