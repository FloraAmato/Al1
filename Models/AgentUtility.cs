using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CreaProject.Models
{
    public abstract class AgentUtility
    {
        public int Id { get; set; }

        [Required]
        public int AgentId { get; set; }

        public Agent Agent { get; set; }

        [Required]
        public int GoodId { get; set; }

        public Good Good { get; set; }

        [Required]
        public int DisputeId { get; set; }

        public Dispute Dispute { get; set; }

        [Required]
        [DataType(DataType.Currency)]
        [Column(TypeName = "money")]
        public abstract decimal Utility { get; }
    }
}
