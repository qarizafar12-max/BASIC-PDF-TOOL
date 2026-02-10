from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, 
                                 QTabWidget, QFrame, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

class InfoView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #1A1A1A;
                color: #A0A0A0;
                padding: 10px 20px;
                border: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3E7BFA;
                color: white;
            }
        """)
        
        self.init_about_tab()
        self.init_premium_tab()
        self.init_faq_tab()
        self.init_legal_tab()
        self.init_credits_tab()
        
        layout.addWidget(self.tabs)

    def create_browser(self, content):
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1A1A1A;
                color: #E0E0E0;
                border: none;
                padding: 20px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
        """)
        # Basic Markdown-to-HTML conversion style
        html_content = f"""
        <html>
        <head>
            <style>
                h1 {{ color: #3E7BFA; font-size: 24px; margin-bottom: 10px; }}
                h2 {{ color: #FFFFFF; font-size: 20px; margin-top: 20px; margin-bottom: 10px; }}
                h3 {{ color: #A0A0A0; font-size: 16px; margin-top: 15px; margin-bottom: 5px; }}
                p {{ line-height: 1.6; margin-bottom: 10px; }}
                li {{ margin-bottom: 5px; }}
                .highlight {{ color: #28a745; font-weight: bold; }}
                .warning {{ color: #FF5555; font-weight: bold; }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        browser.setHtml(html_content)
        return browser

    def init_about_tab(self):
        content = """
        <h1>📌 Smart Utility Toolkit — Basic Edition</h1>
        
        <p><b>Smart Utility Toolkit</b> is an all-in-one offline Windows productivity software designed to help users perform daily tasks easily without relying on online websites full of ads, restrictions, and file upload risks.</p>
        
        <h3>This software is made for:</h3>
        <ul>
            <li>Students</li>
            <li>Office workers</li>
            <li>Freelancers</li>
            <li>Small businesses</li>
            <li>General PC users</li>
        </ul>

        <p>Smart Utility Toolkit focuses on: <span class="highlight">✅ Speed, ✅ Simplicity, ✅ Privacy, ✅ Offline functionality, ✅ Professional results</span></p>

        <h2>🎯 Our Mission</h2>
        <p>Our mission is simple:</p>
        <p><b>Provide powerful productivity tools completely offline, fast, safe, and without advertisements.</b></p>

        <h2>👨‍💻 Developer</h2>
        <p><b>Developer Name:</b> <b>MIZ</b><br>
        <b>Edition:</b> Basic (Free Version)</p>

        <h2>🌟 Why Smart Utility Toolkit?</h2>
        <p>Most online tools:<br>
        ❌ show too many ads<br>
        ❌ require internet<br>
        ❌ have daily limits<br>
        ❌ steal user focus<br>
        ❌ risk file privacy</p>
        
        <p>Smart Utility Toolkit solves this problem by providing a robust offline solution.</p>
        
        <hr>
        <p><b>Smart Utility Toolkit — Basic Edition</b><br>
        Developed by <b>MIZ</b><br>
        Support: <a href="https://discord.gg/eyhJBJzjA7" style="color: #3E7BFA;">Discord Support</a> | 03080078400</p>
        """
        self.tabs.addTab(self.create_browser(content), "About")

    def init_premium_tab(self):
        content = """
        <h1>💎 Upgrade to Premium Edition</h1>
        
        <p>Want more power, comfort, and professional tools?</p>
        <p>The <b>Premium Edition</b> is designed for heavy users, offices, freelancers, and businesses.</p>

        <h2>⭐ Premium Edition Benefits</h2>
        <ul>
            <li>✅ Unlock all advanced tools</li>
            <li>✅ Faster processing engine</li>
            <li>✅ Batch processing support</li>
            <li>✅ No limitations</li>
            <li>✅ Premium themes and UI</li>
            <li>✅ Priority support from developer</li>
        </ul>

        <h2>🔥 Premium Features List</h2>
        
        <h3>📌 Advanced PDF Tools</h3>
        <ul>
            <li>PDF Password Lock / Unlock</li>
            <li>PDF Watermark Add / Remove</li>
            <li>PDF Page Rotate / Reorder / Delete</li>
            <li>PDF Repair Tool</li>
            <li>PDF to Word / Excel / PowerPoint</li>
            <li>PDF to Text Extractor</li>
            <li>PDF Compression Pro Mode</li>
        </ul>

        <h3>📌 OCR Pro Tools</h3>
        <ul>
            <li>Batch OCR (multiple images)</li>
            <li>Multi-language OCR</li>
            <li>OCR to Word / PDF export</li>
            <li>Scan Enhancer (noise removal)</li>
        </ul>

        <h3>📌 Advanced Image Tools</h3>
        <ul>
            <li>Image Compressor (high quality)</li>
            <li>Image Converter (PNG/JPG/WebP)</li>
            <li>Image Resizer (bulk resize)</li>
            <li>Image Enhancer Tool</li>
        </ul>

        <h3>📌 File Management Pro</h3>
        <ul>
            <li>Smart Auto File Organizer</li>
            <li>Duplicate Cleaner Pro Mode</li>
            <li>Large File Finder</li>
            <li>Folder Cleanup Tool</li>
            <li>File Encryption / Decryption</li>
        </ul>

        <h3>📌 Productivity & Office Tools</h3>
        <ul>
            <li>Offline Notes Manager</li>
            <li>Password Vault</li>
            <li>Clipboard Manager</li>
            <li>Offline Invoice Generator</li>
            <li>Local Backup Tool</li>
        </ul>

        <h3>📌 Extra Premium Utilities</h3>
        <ul>
            <li>Screen Recorder</li>
            <li>Offline Video Converter</li>
            <li>Internet Speed Test (Optional online)</li>
            <li>Auto Update System</li>
        </ul>

        <h2>🏆 Premium Support</h2>
        <ul>
            <li>✅ Direct developer support</li>
            <li>✅ Faster bug fixes</li>
            <li>✅ Early access to new tools</li>
            <li>✅ Premium updates</li>
        </ul>

        <h2>📞 Contact for Premium</h2>
        <p><b>Phone / WhatsApp:</b> 03080078400<br>
        <b>Discord Support:</b> <a href="https://discord.gg/eyhJBJzjA7" style="color: #3E7BFA;">Join Discord Server</a></p>
        
        <h3>Premium Plans:</h3>
        <ul>
            <li>Monthly plan</li>
            <li>Yearly plan</li>
            <li>Lifetime plan (limited offer)</li>
        </ul>
        """
        self.tabs.addTab(self.create_browser(content), "Premium")

    def init_faq_tab(self):
        content = """
        <h1>❓ FAQ (Frequently Asked Questions)</h1>

        <h3>Q1: Is Smart Utility Toolkit completely offline?</h3>
        <p>✅ Yes. Most tools work offline. Only optional features like online updates require internet.</p>

        <h3>Q2: Are my files safe?</h3>
        <p>✅ Yes. Your files stay on your computer. We do not upload or store user data.</p>

        <h3>Q3: Why is this software free?</h3>
        <p>The Basic version is free to help users avoid online ads and limitations. Premium features support future development.</p>

        <h3>Q4: Does it support Windows 10 and Windows 11?</h3>
        <p>✅ Yes. Smart Utility Toolkit supports Windows 10/11.</p>

        <h3>Q5: Can I use it for office work?</h3>
        <p>Yes, Basic version is suitable for normal tasks. For advanced office needs, Premium is recommended.</p>

        <h3>Q6: How can I report a bug?</h3>
        <p>Join Discord and report it in the bug channel or contact via phone.</p>

        <h3>Q7: Will Premium Edition be lifetime?</h3>
        <p>Premium options will include Monthly, Yearly, and Lifetime plans.</p>
        """
        self.tabs.addTab(self.create_browser(content), "FAQ")

    def init_legal_tab(self):
        content = """
        <h1>🛡️ Legal Information</h1>

        <h2>📜 License & Usage Policy</h2>
        <p>Smart Utility Toolkit (Basic Edition) is free to use for personal and educational purposes.</p>

        <h3>✅ Allowed</h3>
        <ul>
            <li>Free use on personal computers</li>
            <li>Use in schools and offices (basic usage)</li>
            <li>Sharing the software with friends</li>
        </ul>

        <h3>❌ Not Allowed</h3>
        <ul>
            <li>Selling this software without permission</li>
            <li>Re-uploading on websites without credit</li>
            <li>Modifying and distributing the modified version</li>
            <li>Claiming ownership of this software</li>
        </ul>
        <p>For commercial and premium use, users should upgrade to the Premium Edition.</p>

        <hr>

        <h2>🔐 Privacy Policy</h2>
        <p>Smart Utility Toolkit respects user privacy.</p>

        <h3>We do NOT:</h3>
        <ul>
            <li>❌ collect user files</li>
            <li>❌ upload documents</li>
            <li>❌ track activity</li>
            <li>❌ show ads</li>
            <li>❌ sell user data</li>
        </ul>

        <h3>We ONLY:</h3>
        <ul>
            <li>✅ process files locally on your PC</li>
            <li>✅ store settings locally if user saves them</li>
        </ul>

        <hr>

        <h2>📌 Terms of Use</h2>
        <p>By using Smart Utility Toolkit, you agree:</p>
        <ul>
            <li>You are responsible for the files you process.</li>
            <li>Always keep backup of important documents.</li>
            <li>Developer is not responsible for damage caused by corrupted files.</li>
            <li>You will not misuse the software for illegal activities.</li>
            <li>Premium tools require a valid license key.</li>
        </ul>
        """
        self.tabs.addTab(self.create_browser(content), "Legal")

    def init_credits_tab(self):
        content = """
        <h1>🏅 Credits</h1>

        <p><b>Smart Utility Toolkit</b> is developed and maintained by:</p>
        <h2>👨‍💻 MIZ</h2>

        <h3>Special thanks to:</h3>
        <ul>
            <li>Community testers</li>
            <li>Users who provide feedback</li>
            <li>Open-source libraries used for PDF/OCR features (PyMuPDF, EasyOCR, Qt)</li>
        </ul>
        """
        self.tabs.addTab(self.create_browser(content), "Credits")
