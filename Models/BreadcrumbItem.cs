namespace CreaProject.Models
{
    public class BreadcrumbStep
    {
        public string Title { get; set; }
        public string Url { get; set; }
        public BreadcrumbState State { get; set; }
    }


    public enum BreadcrumbState
    {
        Completed,
        Inactive,
        Ongoing,
        Rejected
    }
}
