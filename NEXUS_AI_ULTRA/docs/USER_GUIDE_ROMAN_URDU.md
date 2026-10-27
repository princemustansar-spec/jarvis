# NEXUS istemal karne ka tareeqa

1. Python 3.11 ya 3.12 64-bit version install karein. Project extract karein.
2. `INSTALL.bat` par double-click karein. Error aaye to console ka paigham dekhein.
3. `START_NEXUS.bat` kholein. Dashboard apni pywebview desktop window mein khulega; default browser app launch par nahin khulega.
4. Settings mein apna provider, API base aur exact model configure karein. API key sirf app ke password field mein dein; chat ya source mein nahin.
5. Save karein, phir endpoint Test karein. “Not verified” ka matlab connection abhi sabit nahin hua. Models ki list se asal model name use karein.
6. Paid provider ke liye har request se pehle “Allow paid request” khud select karein. Charges provider ki policy ke mutabiq honge.
7. AI Chat mein English ya Roman Urdu sawal likhein. Provider ke baghair app fake AI jawab nahin degi; local tools phir bhi chalenge.
8. Files ke liye Settings mein sirf zaroori folders approve karein. Computer Control mein path aur doosri details dein. Sensitive action ko Safety Center mein exact arguments dekh kar Approve ya Deny karein.
9. Teach AI / Knowledge & Memory mein sirf woh baat save karein jo aap future conversations mein istemal karwana chahte hain. Is se model retrain nahin hota.
10. Reminders mein title aur future waqt dein. App chal rahi ho to waqt par in-app notification aayegi. Band ho to aglay start par overdue reminder milega.
11. Voice Assistant mein Start microphone dabayein aur browser permission dein. Browser audio ko apni speech service bhej sakta hai. Transcript review karke Send karein. Mic khud ba-khud background mein nahin chalta.
12. WhatsApp Center sirf draft kholta hai. Send aap WhatsApp mein khud karein.
13. Media Studio ke liye image API aur image model zaroori hain. Video editing is version mein available nahin.
14. Emergency Stop se active AI request aur pending approvals rokein. Pehle ho chuki action ya paid remote request undo nahin hoti. Safety Center se Resume karein.
15. App band karne ke liye desktop window close karein; is se local backend bhi stop hota hai. Emergency ke liye `STOP_NEXUS.bat` hai.

RAM monitor asli numbers dikhata hai. “RAM boost” ke naam par apps band nahin hotin. Windows-only tool cloud Linux machine par unsupported ka message dega.


Desktop shortcut INSTALL.bat banata hai. Dobara banane ke liye CREATE_DESKTOP_SHORTCUT.bat chalayein. WebView2 missing ka error aaye to Microsoft ki website se WebView2 Evergreen Runtime install karein. Browser khol kar app chalana ab zaroori nahin.

Portable EXE ke liye Windows par BUILD_WINDOWS.bat chalayein. dist\NEXUS_AI_ULTRA ka POORA folder doosray PC par copy karein, sirf EXE nahin. Us PC par Python zaroori nahin, lekin WebView2 runtime zaroori hai. Is Linux cloud mein Windows EXE build aur asli window ka test nahin hua.
