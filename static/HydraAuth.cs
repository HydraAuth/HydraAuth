using System;
using System.Net.Http;
using System.Collections.Generic;
using Newtonsoft.Json;
using System.Text;
using System.Threading.Tasks;

public static class HydraAuth
{
    public static dynamic response;
    private static readonly string apiUrl = "https://hydraauth.onrender.com/client_login";
    private static readonly string category = "SAGAR"; // <- Change this if needed

    private static string GetHWID()
    {
        return Environment.MachineName; // Simple HWID placeholder
    }

    public static void login(string username, string password)
    {
        using (var client = new HttpClient())
        {
            var values = new Dictionary<string, string>
            {
                { "category", category },
                { "username", username },
                { "password", password },
                { "hwid", GetHWID() }
            };

            var content = new FormUrlEncodedContent(values);
            try
            {
                var responseMessage = client.PostAsync(apiUrl, content).Result;
                string resultString = responseMessage.Content.ReadAsStringAsync().Result;
                response = JsonConvert.DeserializeObject(resultString);
            }
            catch (Exception ex)
            {
                response = new { success = false, message = "Connection error: " + ex.Message };
            }
        }
    }
}