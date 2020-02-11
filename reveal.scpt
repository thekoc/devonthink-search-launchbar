on run argv
    tell application "DEVONthink 3"
        local theRecord, theParent
        set theUuid to item 1 of argv
        set theRecord to get record with uuid theUuid
        set theParent to item 1 of (parents of theRecord)
        
        set theWindow to open window for record theParent
        
        set myList to {theRecord}
        
        set theWindow's selection to myList
    end tell
end run