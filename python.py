import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import yt_dlp as youtube_dl
import os

def get_video_quality_options(url):
    """Fetch available quality options for the given URL."""
    try:
        # Get video info without downloading
        with youtube_dl.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
        
        # Extract video resolutions (available streams)
        quality_options = []
        for stream in info_dict['formats']:
            if 'height' in stream:
                quality_options.append(f"{stream['height']}p")
        
        # Remove duplicates and sort by resolution
        quality_options = sorted(set(quality_options), key=lambda x: int(x[:-1]))
        return quality_options
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch quality options: {str(e)}")
        return []

def download_video():
    url = url_entry.get()
    if not url.strip():
        messagebox.showwarning("Input Error", "Please enter a valid YouTube URL.")
        return

    try:
        # Ask for download location
        download_path = filedialog.askdirectory()
        if not download_path:
            return
        
        # Get the selected video quality
        selected_quality = quality_combobox.get()

        # yt-dlp download options
        ydl_opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'format': f'bestvideo[height={selected_quality[:-1]}]+bestaudio/best',  # Select video with matching resolution
            'progress_hooks': [progress_hook],  # Progress hook to update the progress bar
            'noplaylist': True,  # Ensure only one video is downloaded
        }

        # Download using yt-dlp
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        messagebox.showinfo("Success", "Video downloaded successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to download video: {str(e)}")


# Progress hook function to update the progress bar
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = float(d['downloaded_bytes']) / float(d['total_bytes']) * 100
        progress_var.set(percent)  # Update progress bar value
        root.update_idletasks()  # Ensure the UI updates in real-time
    elif d['status'] == 'finished':
        progress_var.set(100)  # Set the progress bar to 100% when download is finished
        root.update_idletasks()


# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")

# URL Entry
tk.Label(root, text="Enter YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Quality Selection Dropdown
tk.Label(root, text="Select Quality:").pack(pady=5)
quality_combobox = ttk.Combobox(root, values=["360p", "480p", "720p", "1080p"])
quality_combobox.set("360p")  # Default quality
quality_combobox.pack(pady=5)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=400)
progress_bar.pack(pady=10)

# Download Button
download_button = tk.Button(root, text="Download", command=download_video)
download_button.pack(pady=10)

# Update quality options based on the URL entered
def update_quality_options():
    url = url_entry.get()
    if url.strip():
        options = get_video_quality_options(url)
        quality_combobox['values'] = options
        if options:
            quality_combobox.set(options[0])  # Set default to the first option
    else:
        messagebox.showwarning("Input Error", "Please enter a valid YouTube URL to fetch quality options.")

# Monitor URL input for quality updates
url_entry.bind("<KeyRelease>", lambda event: update_quality_options())

# Run the application
root.mainloop()
