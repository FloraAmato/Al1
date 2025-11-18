using CreaProject.Areas.Identity;
using CreaProject.Areas.Identity.Data;
using CreaProject.Data;
using Microsoft.AspNetCore.Hosting;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

[assembly: HostingStartup(typeof(IdentityHostingStartup))]

namespace CreaProject.Areas.Identity
{
    public class IdentityHostingStartup : IHostingStartup
    {
        public void Configure(IWebHostBuilder builder)
        {
            builder.ConfigureServices((context, services) =>
            {
                services.AddDbContext<ApplicationDbContext>(options =>
                    options.UseSqlServer(
                        context.Configuration.GetConnectionString("DefaultConnection")));

                services.AddDefaultIdentity<CreaUser>(options => options.SignIn.RequireConfirmedAccount = true)
                    .AddEntityFrameworkStores<ApplicationDbContext>();
            });
        }
    }
}