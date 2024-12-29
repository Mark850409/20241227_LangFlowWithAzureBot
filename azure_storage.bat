set AZURE_KEY=<自己的金鑰>
net use Z: "\\langflowdata.file.core.windows.net\langflowdata" /user:Azure\langflowdata %AZURE_KEY% /persistent:Yes
