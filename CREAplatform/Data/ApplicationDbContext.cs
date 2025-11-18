using CreaProject.Areas.Identity.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace CreaProject.Data
{
    public class ApplicationDbContext : IdentityDbContext<CreaUser>
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }


        public DbSet<Dispute> Disputes { get; set; }
        public DbSet<Agent> Agents { get; set; }
        public DbSet<Good> Goods { get; set; }
        public DbSet<Bid> Bids { get; set; }
        public DbSet<Rate> Rates { get; set; }
        
        public DbSet<RestrictedAssignment> RestrictedAssignments { get; set; }

        protected override void OnModelCreating(ModelBuilder builder)
        {
            base.OnModelCreating(builder);
            // Customize the ASP.NET Identity model and override the defaults if needed.
            // For example, you can rename the ASP.NET Identity table names and more.
            // Add your customizations after calling base.OnModelCreating(builder);


            builder.Entity<Agent>().HasIndex(p => new {p.Email, p.DisputeId}).IsUnique();
            builder.Entity<Good>().HasIndex(p => new {p.Name, p.DisputeId}).IsUnique();

            builder.Entity<AgentUtility>().ToTable("AgentUtilities");
            builder.Entity<Bid>().HasIndex(p => new {p.AgentId, p.DisputeId, p.GoodId}).IsUnique();
            builder.Entity<Rate>().HasIndex(p => new {p.AgentId, p.DisputeId, p.GoodId}).IsUnique();

            builder.Entity<AgentUtility>()
                .HasOne(u => u.Good)
                .WithMany(u => u.AgentUtilities)
                .IsRequired()
                .OnDelete(DeleteBehavior.Restrict);

            builder.Entity<AgentUtility>()
                .HasOne(u => u.Dispute)
                .WithMany(u => u.AgentUtilities)
                .IsRequired()
                .OnDelete(DeleteBehavior.Restrict);
            
            builder.Entity<RestrictedAssignment>()
                .HasOne(u => u.Dispute)
                .WithMany(u => u.RestrictedAssignments)
                .IsRequired()
                .OnDelete(DeleteBehavior.Restrict);
            
            builder.Entity<RestrictedAssignment>()
                .HasOne(u => u.Good)
                .WithMany(u => u.RestrictedAssignments)
                .IsRequired()
                .OnDelete(DeleteBehavior.Restrict);
                
            builder.Entity<RestrictedAssignment>()
                .HasOne(u => u.Agent)
                .WithMany(u => u.RestrictedAssignments)
                .IsRequired()
                .OnDelete(DeleteBehavior.Restrict);
           
        }
    }
}