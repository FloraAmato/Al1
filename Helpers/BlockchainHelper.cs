using Azure.Identity;
using Mailjet.Client;
using Microsoft.SqlServer.Server;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Dynamic;
using System.Globalization;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;

namespace CreaProject.Helpers
{
    public class BlockchainHelper
    {
        private string _token;
        private HttpClient _httpClient;

        public BlockchainHelper()
        {
            _httpClient = new HttpClient();
            _httpClient.BaseAddress = new System.Uri("https://chain.scan2project.org");
        }

        private async Task<bool> Login()
        {
            var path = new Uri(_httpClient.BaseAddress, "auth/v1/login");
            dynamic d = new ExpandoObject();
            d.username = "khramov1";
            d.password = "123456";

            using (HttpResponseMessage response = await this._httpClient.PostAsync(path, new StringContent(JsonConvert.SerializeObject(d), Encoding.UTF8, "application/json"), CancellationToken.None))
            {

                LoginResponse loginResponse = await response.Content.ReadFromJsonAsync<LoginResponse>(CancellationToken.None);
                _token = loginResponse.Data.Token;
                return response.IsSuccessStatusCode;
            }
        }

        public class LoginResponse
        {
            [JsonProperty("status")]
            [JsonPropertyName("status")]
            public string Status { get; set; }

            [JsonProperty("message")]
            [JsonPropertyName("message")]
            public string Message { get; set; }

            [JsonProperty("data")]
            [JsonPropertyName("data")]
            public LoginResponseData Data { get; set; }

            public class LoginResponseData
            {
                [JsonProperty("username")]
                [JsonPropertyName("username")]
                public string Username { get; set; }

                [JsonProperty("token")]
                [JsonPropertyName("token")]
                public string Token { get; set; }
            }
        }

        public class AnchorResponse
        {

            [JsonProperty("data")]
            [JsonPropertyName("data")]
            public AnchorData Data { get; set; }


            [JsonProperty("links")]
            [JsonPropertyName("links")]
            public Links Link { get; set; }

            public class Links
            {

                [JsonProperty("self")]
                [JsonPropertyName("self")]
                public string Self { get; set; }
            }

            public class AnchorData
            {
                [JsonProperty("id")]
                [JsonPropertyName("id")]
                public string Id { get; set; }

                [JsonProperty("type")]
                [JsonPropertyName("type")]
                public string Type { get; set; }

                [JsonProperty("uuid")]
                [JsonPropertyName("uuid")]
                public string uuid { get; set; }

                [JsonProperty("entry_data_hash")]
                [JsonPropertyName("entry_data_hash")]
                public string EntryDataHash { get; set; }

                [JsonProperty("owner")]
                [JsonPropertyName("owner")]
                public string owner { get; set; }

                [JsonProperty("metadata")]
                [JsonPropertyName("metadata")]
                public Metadata MetaData { get; set; }

                [JsonProperty("entry_kind")]
                [JsonPropertyName("entry_kind")]
                public string EntryKind { get; set; }
                public class Metadata
                {
                    [JsonProperty("created_at")]
                    [JsonPropertyName("created_at")]
                    public DateTime? CreatedAt { get; set; }

                    [JsonProperty("updated_at")]
                    [JsonPropertyName("updated_at")]
                    public DateTime? UpdatedAt { get; set; }
                }

                [JsonProperty("entry_data")]
                [JsonPropertyName("entry_data")]
                public object EntryData { get; set; }
            }
        }

        public async Task<string> AnchorData( string username,object data)
        {
            await Login();
            var path = new Uri(_httpClient.BaseAddress, "blockchain_store/v1/entries");
            _httpClient.UseBearerAuthentication(_token);

            dynamic d = new ExpandoObject();

            d.data = new ExpandoObject();
            d.data.type = "entry";
            d.data.entry_data_hash = "hash1";
            d.data.owner = username;
            d.data.entry_kind = "dispute_solution";
            d.data.entry_data = data;


            JsonSerializerSettings settings = new JsonSerializerSettings();
            settings.NullValueHandling = NullValueHandling.Ignore;
            settings.ReferenceLoopHandling = ReferenceLoopHandling.Ignore;

            using (HttpResponseMessage response = await _httpClient.PostAsync(path, new StringContent(JsonConvert.SerializeObject(d, settings), Encoding.UTF8, "application/json")))
            {
                AnchorResponse responseObject = await response.Content.ReadFromJsonAsync<AnchorResponse>(CancellationToken.None);
                return responseObject.Data.Id;
            }
        }

    }
}
