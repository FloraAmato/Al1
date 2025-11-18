using Microsoft.EntityFrameworkCore.Migrations;

namespace CreaProject.Migrations
{
    public partial class share : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterColumn<double>(
                name: "ShareOfEntitlement",
                table: "Agents",
                nullable: true,
                oldClrType: typeof(decimal),
                oldType: "decimal(3, 2)"
            );
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterColumn<decimal>(
                name: "ShareOfEntitlement",
                table: "Agents",
                type: "decimal(3, 2)",
                nullable: false,
                oldClrType: typeof(double),
                oldNullable: true
            );
        }
    }
}
