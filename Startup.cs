using System;
using CreaProject.Authorization;
using CreaProject.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Localization;
using Microsoft.AspNetCore.Mvc.Authorization;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System.Collections.Generic;
using System.Globalization;
using Azure.Extensions.AspNetCore.Configuration.Secrets;
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using CreaProject.Helpers;

namespace CreaProject
{
    public class Startup
    {
        private IWebHostEnvironment _env;
        public Startup(IConfiguration configuration, IWebHostEnvironment env)
        {
            Configuration = configuration;
            _env = env;
        }

        private IConfiguration Configuration { get; set; }

        public void ConfigureServices(IServiceCollection services)
        {
            string connectionString = _env.IsDevelopment() ? Configuration["DatabaseUrlLocal"] : Configuration["DatabaseUrl"];
            services.AddDbContext<ApplicationDbContext>(options =>
                options.UseSqlServer(connectionString)
            );

            services.Configure<CookiePolicyOptions>(options =>
            {
                options.CheckConsentNeeded = context => true;
                options.MinimumSameSitePolicy = SameSiteMode.None;
                options.ConsentCookieValue = "true";
            });

            services.AddLocalization(options => options.ResourcesPath = "Resources");
            services.AddRazorPages().AddViewLocalization();
            services.AddControllersWithViews();
            services.AddAntiforgery(o => o.HeaderName = "XSRF-TOKEN");

            services.AddControllers(config =>
            {
                AuthorizationPolicy policy = new AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build();
                config.Filters.Add(new AuthorizeFilter(policy));
            });

            services.AddMvcCore().AddDataAnnotations();

            services.AddAuthorizationBuilder()
                .AddPolicy("DisputeAgentPolicy", policy => policy.Requirements.Add(new OperationAuthorizationRequirement()));

            services.AddScoped<IAuthorizationHandler, ContactIsOwnerAuthorizationHandler>();

            services.AddScoped<IAuthorizationHandler, ContactIsAgentAuthorizationHandler>();

            services.AddSingleton<
                IAuthorizationHandler,
                ContactAdministratorsAuthorizationHandler
            >();

            services.AddSingleton<IAuthorizationHandler, ContactManagerAuthorizationHandler>();

            services.ConfigureApplicationCookie(options =>
            {
                options.LoginPath = new PathString("/Identity/Account/Login");
            });

            services.AddTransient<MailjetService>();
            services.AddTransient<BlockchainHelper>();
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            List<CultureInfo> supportedCultures =
            [
                new CultureInfo("en-US"),
                new CultureInfo("fr")
            ];
            RequestLocalizationOptions options = new()
            {
                DefaultRequestCulture = new RequestCulture("en-US"),
                SupportedCultures = supportedCultures,
                SupportedUICultures = supportedCultures,
            };
            app.UseRequestLocalization(options);
            app.UseRouting();
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
                app.UseDatabaseErrorPage();
            }
            else
            {
                //app.UseExceptionHandler("/Error");
                app.UseDeveloperExceptionPage();
                app.UseHsts();
            }

            app.UseHttpsRedirection();
            app.UseStaticFiles();

            app.UseAuthentication();
            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
                endpoints.MapRazorPages();
                endpoints.MapControllerRoute(
                    name: "default",
                    pattern: "{controller=Home}/{action=Index}/{id?}");
            });
        }
    }
}
