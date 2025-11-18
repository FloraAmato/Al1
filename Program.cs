using System;
using Azure.Identity;
using CreaProject.Data;
using Microsoft.AspNetCore.Hosting;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace CreaProject
{
    #region snippet

    public class Program
    {
        public static void Main(string[] args)
        {
            IHost host = CreateHostBuilder(args).Build();

            using (IServiceScope scope = host.Services.CreateScope())
            {
                IServiceProvider services = scope.ServiceProvider;

                try
                {
                    ApplicationDbContext context = services.GetRequiredService<ApplicationDbContext>();

                    context.Database.Migrate();

                    // requires using Microsoft.Extensions.Configuration;
                    IConfiguration config = host.Services.GetRequiredService<IConfiguration>();
                    // Set password with the Secret Manager tool.
                    // dotnet user-secrets set SeedUserPW <pw>

                    string testUserPw = config["SeedUserPW"];

                    SeedData.Initialize(services, testUserPw).Wait();
                }
                catch (Exception ex)
                {
                    ILogger<Program> logger = services.GetRequiredService<ILogger<Program>>();
                    logger.LogError(ex, "An error occurred seeding the DB.");
                }
            }

            host.Run();
        }

        private static IHostBuilder CreateHostBuilder(string[] args)
        {
            return Host.CreateDefaultBuilder(args)
                .ConfigureAppConfiguration((context, config) =>
                {
                    IConfigurationRoot builtConfig = config.Build();
                    string keyVaultUrl = builtConfig["KeyVaultUrl"];
                    if (!string.IsNullOrEmpty(keyVaultUrl))
                    {
                        var credentials = new DefaultAzureCredential();
                        config.AddAzureKeyVault(new Uri(keyVaultUrl), credentials);
                    }
                })
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                });
        }
    }

    #endregion
}
