using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows.Forms;

namespace NewBuildGovernanceAgent
{
    internal static class Launcher
    {
        private const string ProductName = "New Build Governance Agent";

        [STAThread]
        private static int Main()
        {
            Application.EnableVisualStyles();

            string repoRoot = FindRepoRoot(AppDomain.CurrentDomain.BaseDirectory);
            if (string.IsNullOrEmpty(repoRoot))
            {
                ShowError(
                    "Unable to find automation\\launch_gui.ps1.\n\n" +
                    "Unzip the full New Build Governance Agent Windows package, then double-click " +
                    "NewBuildGovernanceAgent.exe from inside that folder."
                );
                return 1;
            }

            string launcher = Path.Combine(repoRoot, "automation", "launch_gui.ps1");
            string logPath = Path.Combine(repoRoot, "data", "new-build-governance-agent", "logs", "gui-launch-windows.log");

            try
            {
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = "-NoProfile -ExecutionPolicy Bypass -File " + Quote(launcher),
                    WorkingDirectory = repoRoot,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WindowStyle = ProcessWindowStyle.Hidden
                };

                using (Process process = Process.Start(startInfo))
                {
                    if (process == null)
                    {
                        ShowError("Windows could not start PowerShell.");
                        return 1;
                    }

                    process.WaitForExit();
                    if (process.ExitCode != 0)
                    {
                        ShowError(BuildFailureMessage(process.ExitCode, logPath));
                        return process.ExitCode;
                    }
                }
            }
            catch (Exception ex)
            {
                ShowError("Unable to launch the desktop GUI.\n\n" + ex.Message);
                return 1;
            }

            return 0;
        }

        private static string FindRepoRoot(string startDirectory)
        {
            DirectoryInfo current = new DirectoryInfo(startDirectory);
            while (current != null)
            {
                string launcher = Path.Combine(current.FullName, "automation", "launch_gui.ps1");
                if (File.Exists(launcher))
                {
                    return current.FullName;
                }
                current = current.Parent;
            }

            return string.Empty;
        }

        private static string BuildFailureMessage(int exitCode, string logPath)
        {
            StringBuilder message = new StringBuilder();
            message.AppendLine("The desktop GUI did not start.");
            message.AppendLine();
            message.AppendLine("Exit code: " + exitCode);

            if (File.Exists(logPath))
            {
                string log = File.ReadAllText(logPath).Trim();
                if (!string.IsNullOrEmpty(log))
                {
                    message.AppendLine();
                    message.AppendLine("Latest launcher log:");
                    message.AppendLine(TrimForDialog(log, 1800));
                }
            }
            else
            {
                message.AppendLine();
                message.AppendLine("No launcher log was found at:");
                message.AppendLine(logPath);
            }

            message.AppendLine();
            message.AppendLine("Make sure Python 3.8 or newer is installed from python.org with Tcl/Tk support enabled.");
            return message.ToString();
        }

        private static string TrimForDialog(string value, int maxLength)
        {
            if (value.Length <= maxLength)
            {
                return value;
            }
            return value.Substring(0, maxLength) + "\n...";
        }

        private static string Quote(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }

        private static void ShowError(string message)
        {
            MessageBox.Show(message, ProductName, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
}
