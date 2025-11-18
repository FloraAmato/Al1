using CreaProject.Areas.Identity.Data;
using System.ComponentModel.DataAnnotations;

namespace CreaProject.Models
{
    public class Conversation
    {
        public int ConversationId { get; set; }

        [Required]
        public string UserId { get; set; }

        public CreaUser User { get; set; }

        [Required]
        public string SessionId { get; set; }
    }
}
