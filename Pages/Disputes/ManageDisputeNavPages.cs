using System;
using System.IO;
using CreaProject.Models;
using Microsoft.AspNetCore.Mvc.Rendering;

namespace CreaProject.Pages.Disputes
{
    public static class ManageDisputeNavPages
    {
        public static string Details => "Edit";

        public static string Agents => "Agents";

        public static string Goods => "Goods";

        public static string Bids => "Bids";
        public static string Rates => "Rates";

        public static string Solution => "Solution";

        public static string DetailsNavActiveClass(ViewContext viewContext)
        {
            return PageNavActiveClass(viewContext, Details);
        }

        public static string DetailsPageUrl(Dispute dispute)
        {
            return PageUrl(dispute, "Edit");
        }

        public static string AgentsNavActiveClass(ViewContext viewContext)
        {
            return PageNavActiveClass(viewContext, Agents);
        }

        public static string AgentsPageUrl(Dispute dispute)
        {
            return PageUrl(dispute, "EditAgents");
        }

        public static string GoodsNavActiveClass(ViewContext viewContext)
        {
            return PageNavActiveClass(viewContext, Goods);
        }

        public static string GoodsPageUrl(Dispute dispute)
        {
            return PageUrl(dispute, "EditGoods");
        }

        public static string BidsNavActiveClass(ViewContext viewContext)
        {
            return PageNavActiveClass(viewContext, Bids);
        }

        public static string BidsPageUrl(Dispute dispute)
        {
            return PageUrl(dispute, "EditBids");
        }

        public static string RatesNavActiveClass(ViewContext viewContext)
        {
            return PageNavActiveClass(viewContext, Rates);
        }

        public static string RatesPageUrl(Dispute dispute)
        {
            return PageUrl(dispute, "EditRates");
        }

        public static string SolutionNavActiveClass(ViewContext viewContext)
        {
            return PageNavActiveClass(viewContext, Solution);
        }

        public static string SolutionPageUrl(Dispute dispute)
        {
            return PageUrl(dispute, "Solution");
        }

        private static string PageNavActiveClass(ViewContext viewContext, string page)
        {
            var activePage =
                viewContext.ViewData["ActivePage"] as string
                ?? Path.GetFileNameWithoutExtension(viewContext.ActionDescriptor.DisplayName);
            return string.Equals(activePage, page, StringComparison.OrdinalIgnoreCase)
                ? "active"
                : null;
        }

        private static string PageUrl(Dispute dispute, string page)
        {
            var disputeId = dispute.DisputeId;
            return string.Concat($"/Disputes/{page}/{disputeId}");
        }
    }
}
