# 🍅 Pomodoro Timer

A modern, feature-rich Pomodoro timer application built with PyQt6. This professional-grade timer helps you boost productivity using the proven Pomodoro Technique.

## ✨ Features

### 🎯 Core Functionality
- **Classic Pomodoro Timer**: 25-minute work sessions with 5-minute breaks
- **Auto Mode**: Seamless transitions between work and break periods
- **Flexible Timing**: Customizable work and break durations
- **Session Tracking**: Comprehensive statistics and progress monitoring

### 🎨 Modern Interface
- **Responsive Design**: Adapts to different screen sizes and resolutions
- **Dark/Light Themes**: Multiple beautiful themes to match your preference
- **Floating Widget**: Compact timer widget that stays on top
- **Smooth Animations**: Engaging visual feedback and transitions

### 📊 Advanced Features
- **Detailed Statistics**: Track daily, weekly, and monthly progress
- **Visual Charts**: Interactive graphs showing productivity trends
- **Session History**: Complete log of all completed sessions
- **Data Persistence**: All settings and statistics automatically saved

### 🔔 Notifications
- **System Notifications**: Desktop alerts for session changes
- **Sound Alerts**: Customizable audio notifications
- **Visual Indicators**: Color-coded progress indicators
- **System Tray Integration**: Quick access from system tray

## 🚀 Installation

### Option 1: Pre-built Executables (Recommended)

Download the latest release for your operating system:
- **Windows**: `pomodoro-timer-windows.exe`
- **macOS**: `pomodoro-timer-macos.app`
- **Linux**: `pomodoro-timer-linux.AppImage`

### Option 2: From Source

#### Prerequisites
- Python 3.8 or higher
- pip package manager

#### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/pomodoro-timer.git
   cd pomodoro-timer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python src/main.py
   ```

#### Building Executables

To create standalone executables:

```bash
# Install build dependencies
pip install -r requirements.txt

# Build for current platform
python build.py

# Executables will be created in the 'dist' directory
```

## 📱 Usage

### Getting Started

1. **Launch the application** - Either run the executable or use `python src/main.py`
2. **Choose your mode**:
   - **Manual Mode**: Start/pause sessions manually
   - **Auto Mode**: Automatic transitions between work and breaks
3. **Start your first session** - Click the play button to begin

### Main Interface

#### Timer Page
- **Central Timer**: Large, easy-to-read countdown display
- **Control Buttons**: Start, pause, reset, and skip session controls
- **Progress Indicator**: Visual progress bar showing session completion
- **Session Info**: Current session type (Work/Break) and cycle count

#### Settings Page
- **Timer Settings**: Customize work and break durations
- **Appearance**: Choose themes and enable animations
- **Notifications**: Configure sound and desktop alerts
- **Auto Mode**: Enable seamless session transitions

#### Statistics Page
- **Progress Charts**: Visual representation of your productivity
- **Session Summary**: Today's completed sessions and total time
- **Historical Data**: Weekly and monthly progress tracking
- **Productivity Metrics**: Success rates and consistency indicators

### Floating Widget

For a minimal, always-on-top experience:

1. Click the **"Float"** button in the main window
2. The compact floating widget will appear
3. Drag it anywhere on your screen
4. Double-click to return to the main window

## ⚙️ Configuration

### Settings File

All settings are automatically saved to:
- **Windows**: `%APPDATA%/PomodoroTimer/config.json`
- **macOS**: `~/Library/Application Support/PomodoroTimer/config.json`
- **Linux**: `~/.config/PomodoroTimer/config.json`

### Customizable Options

#### Timer Settings
- Work duration (default: 25 minutes)
- Short break duration (default: 5 minutes)
- Long break duration (default: 15 minutes)
- Sessions before long break (default: 4)

#### Appearance Settings
- Theme selection (Light/Dark/Auto)
- Animation preferences
- Window opacity
- Color schemes

#### Notification Settings
- Desktop notifications (on/off)
- Sound notifications (on/off)
- Custom notification sounds
- Notification timing

## 🎨 Themes

### Available Themes
- **Light Theme**: Clean, bright interface for daytime use
- **Dark Theme**: Easy on the eyes for low-light environments
- **Auto Theme**: Automatically switches based on system preferences

### Customization
- Accent colors can be customized in the settings
- Animation speed and effects are adjustable
- Window transparency options available

## 📊 Statistics and Data

### Data Tracking
- Session completion times
- Break adherence rates
- Daily productivity patterns
- Weekly and monthly summaries

### Export Options
- Statistics can be exported as CSV files
- Data visualization screenshots
- Printable productivity reports

### Privacy
- All data is stored locally on your device
- No data collection or transmission to external servers
- Complete control over your productivity data

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start
- Ensure Python 3.8+ is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Try running from command line to see error messages

#### Notifications Not Working
- Check system notification permissions
- Verify notification settings in the app
- On macOS, grant notification permissions in System Preferences

#### Floating Widget Issues
- Try minimizing and restoring the main window
- Check if the widget is hidden behind other windows
- Restart the application if the widget becomes unresponsive

#### Data Not Saving
- Ensure the application has write permissions to config directory
- Check available disk space
- Verify config directory exists and is accessible

### Performance Optimization

For best performance:
- Close unnecessary applications while using the timer
- Disable animations if experiencing lag
- Use the floating widget for minimal resource usage

## 🛠️ Development

### Project Structure

```
pomodoro-timer/
├── src/
│   ├── main.py              # Application entry point
│   ├── config/              # Configuration management
│   ├── core/               # Timer logic and data management
│   ├── ui/                 # User interface components
│   ├── utils/              # Utilities and system integration
│   └── widgets/            # Custom PyQt6 widgets
├── requirements.txt         # Python dependencies
├── setup.py                # Package configuration
├── build.py                # Build script for executables
└── README.md               # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/pomodoro-timer.git
cd pomodoro-timer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python src/main.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments

- **Pomodoro Technique** created by Francesco Cirillo
- **PyQt6** for the excellent GUI framework
- **Community contributors** for bug reports and feature suggestions

## 📞 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/your-username/pomodoro-timer/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/your-username/pomodoro-timer/discussions)
- **Email**: Contact us at support@pomodorotimer.com

---

**Made with ❤️ for productivity enthusiasts**

*Boost your productivity with the power of focused work sessions!*