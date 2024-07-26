class GlobalData:
    openTabs = []
    globalCalibrations = []
    globalMonitors = []
    
    def notify_all():
        for tab in GlobalData.openTabs:
            tab.verify_buttons()