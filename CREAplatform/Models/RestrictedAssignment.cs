using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CreaProject.Models
{
    public class RestrictedAssignment
    {
        public int Id { get; set; }

        [Required] public int AgentId { get; set; }

        public Agent Agent { get; set; }

        [Required] public int GoodId { get; set; }

        public Good Good { get; set; }

        [Required] public int DisputeId { get; set; }

        public Dispute Dispute { get; set; }

        [Range(0, 100)]
        [Column(TypeName = "decimal(3, 2)")]
        public decimal ShareOfEntitlement { get; set; }
    }
}