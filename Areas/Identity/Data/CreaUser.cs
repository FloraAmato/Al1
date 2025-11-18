using Microsoft.AspNetCore.Identity;

namespace CreaProject.Areas.Identity.Data
{
    // Add profile data for application users by adding properties to the CreaUser class
    public class CreaUser : IdentityUser
    {
        [PersonalData]
        public string Surname { get; set; }

        [PersonalData]
        public string Name { get; set; }
    }
}
