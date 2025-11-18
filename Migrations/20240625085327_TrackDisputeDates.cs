using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CreaProject.Migrations
{
    /// <inheritdoc />
    public partial class TrackDisputeDates : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<DateTime>(
                name: "CreatedAt",
                table: "Disputes",
                type: "datetime2",
                nullable: true,
                defaultValueSql: "GETDATE()");

            migrationBuilder.AddColumn<DateTime>(
                name: "UpdatedAt",
                table: "Disputes",
                type: "datetime2",
                nullable: true,
                defaultValueSql: "GETDATE()");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "CreatedAt",
                table: "Disputes");

            migrationBuilder.DropColumn(
                name: "UpdatedAt",
                table: "Disputes");
        }
    }
}
