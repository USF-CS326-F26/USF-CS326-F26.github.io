/**
 * Enhanced Schedule Table Functionality
 * Features: Reverse order toggle, current week highlighting, smooth navigation
 */

// Initialize schedule functionality
function initSchedule() {
    initReverseOrder();
    initDynamicCurrentWeek();
    initCurrentWeekHighlighting();
    initSmoothNavigation();
}

// Run on initial page load
document.addEventListener('DOMContentLoaded', initSchedule);

// Run when navigating with mkdocs-material instant navigation
// Using the 'location$' observable which is the proper way for MkDocs Material
document$.subscribe(function() {
    // Check if we're on a page with the schedule table
    setTimeout(function() {
        const scheduleTable = document.getElementById('schedule-table');
        if (scheduleTable) {
            initSchedule();
        }
    }, 100);
});

// Also listen for content changes as a fallback
let observer = new MutationObserver(function(mutations) {
    const scheduleTable = document.getElementById('schedule-table');
    if (scheduleTable && !scheduleTable.hasAttribute('data-initialized')) {
        scheduleTable.setAttribute('data-initialized', 'true');
        initSchedule();
        // Remove the attribute after a delay to allow re-initialization on navigation
        setTimeout(function() {
            scheduleTable.removeAttribute('data-initialized');
        }, 500);
    }
});

// Start observing once DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

/**
 * Initialize reverse order functionality for the schedule table
 */
function initReverseOrder() {
    const weekHeader = document.getElementById('week-header');
    const scheduleTable = document.getElementById('schedule-table');
    
    if (weekHeader && scheduleTable) {
        // Check if we already have a click handler to avoid duplicates
        if (weekHeader.hasAttribute('data-click-initialized')) {
            return;
        }
        weekHeader.setAttribute('data-click-initialized', 'true');
        
        // Store state in the element itself
        weekHeader.isReversed = false;
        weekHeader.originalHTML = null;
        
        weekHeader.addEventListener('click', function() {
            const tbody = scheduleTable.querySelector('tbody');
            if (!tbody) return;
            
            // Save original HTML only on first click when not reversed
            if (!this.isReversed && !this.originalHTML) {
                this.originalHTML = tbody.innerHTML;
            }
            
            if (!this.isReversed) {
                // Get all rows
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const weekGroups = [];
                
                // Group rows by week
                // We'll use a simple approach: each group starts with a row that has a week-number with rowspan
                for (let i = 0; i < rows.length; i++) {
                    const weekCell = rows[i].querySelector('.week-number[rowspan]');
                    if (weekCell) {
                        // This is the start of a new week
                        const rowspanCount = parseInt(weekCell.getAttribute('rowspan')) || 3;
                        const group = [];
                        
                        // Collect this week's rows
                        for (let j = 0; j < rowspanCount && i < rows.length; j++) {
                            group.push(rows[i]);
                            i++;
                        }
                        i--; // Adjust because the for loop will increment
                        
                        weekGroups.push(group);
                    }
                }
                
                // Reverse the week order
                weekGroups.reverse();
                
                // For each week group, reverse the days
                const finalGroups = weekGroups.map(group => {
                    // Create a copy and reverse the days
                    return group.slice().reverse();
                });
                
                // Clear tbody
                tbody.innerHTML = '';
                
                // Rebuild the table with reversed order
                finalGroups.forEach((group, groupIndex) => {
                    group.forEach((row, rowIndex) => {
                        const newRow = row.cloneNode(true);
                        
                        // Handle the week number cell
                        const weekCell = newRow.querySelector('.week-number');
                        
                        if (rowIndex === 0) {
                            // This should be the row with the week number
                            if (!weekCell) {
                                // Need to add a week cell from one of the other rows
                                const originalWeekCell = group.find(r => r.querySelector('.week-number'))?.querySelector('.week-number');
                                if (originalWeekCell) {
                                    const newWeekCell = originalWeekCell.cloneNode(true);
                                    newWeekCell.setAttribute('rowspan', group.length.toString());
                                    newRow.insertBefore(newWeekCell, newRow.firstChild);
                                }
                            } else {
                                // Make sure it has the right rowspan
                                weekCell.setAttribute('rowspan', group.length.toString());
                            }
                        } else {
                            // Remove week cell from non-first rows
                            if (weekCell) {
                                weekCell.remove();
                            }
                        }
                        
                        tbody.appendChild(newRow);
                    });
                });
                
                this.isReversed = true;
                this.classList.add('sorted-desc');
                this.title = 'Click to sort chronologically';
                
                // Re-initialize dynamic week detection and highlighting
                initDynamicCurrentWeek();
                initCurrentWeekHighlighting();
            } else {
                // Restore original order
                tbody.innerHTML = this.originalHTML;
                
                this.isReversed = false;
                this.classList.remove('sorted-desc');
                this.title = 'Click to sort in reverse order';
                
                // Re-initialize dynamic week detection and highlighting
                initDynamicCurrentWeek();
                initCurrentWeekHighlighting();
            }
        });
        
        // Set initial tooltip
        weekHeader.title = 'Click to sort in reverse order';
    }
}

/**
 * Dynamically determine and mark the current week based on today's date
 */
function initDynamicCurrentWeek() {
    const today = new Date();
    const currentYear = today.getFullYear();
    let currentWeekNumber = null;
    let minDiff = Infinity;
    let fallbackWeekRows = null;
    
    // First, clear any existing current week markers
    document.querySelectorAll('[data-current-week]').forEach(row => {
        row.removeAttribute('data-current-week');
    });
    
    // Get all rows in the table
    const tbody = document.querySelector('#schedule-table tbody');
    if (!tbody) return;
    
    const allRows = Array.from(tbody.querySelectorAll('tr'));
    const weekGroups = [];
    
    // Group rows by week based on week-number cells with rowspan
    for (let i = 0; i < allRows.length; i++) {
        const weekCell = allRows[i].querySelector('.week-number[rowspan]');
        if (weekCell) {
            // This is the start of a new week
            const weekText = weekCell.textContent.trim();
            const weekMatch = weekText.match(/\d+/);
            const weekNumber = weekMatch ? parseInt(weekMatch[0]) : null;
            const rowspanCount = parseInt(weekCell.getAttribute('rowspan')) || 3;
            const group = {
                weekNumber: weekNumber,
                rows: [],
                dates: []
            };
            
            // Collect this week's rows
            for (let j = 0; j < rowspanCount && i < allRows.length; j++) {
                const row = allRows[i];
                group.rows.push(row);
                
                // Extract date from this row
                const dateCell = row.querySelector('.date-cell strong');
                if (dateCell) {
                    const dateText = dateCell.textContent.trim();
                    try {
                        const parsedDate = new Date(`${dateText} ${currentYear}`);
                        if (!isNaN(parsedDate.getTime())) {
                            group.dates.push(parsedDate);
                        }
                    } catch (e) {
                        console.warn(`Failed to parse date: ${dateText}`);
                    }
                }
                
                i++;
            }
            i--; // Adjust because the for loop will increment
            
            weekGroups.push(group);
        }
    }
    
    // Process each week group to find the current week
    weekGroups.forEach(group => {
        if (group.dates.length === 0) return;
        
        // Sort dates to get the range
        group.dates.sort((a, b) => a - b);
        const firstDate = group.dates[0];
        const lastDate = group.dates[group.dates.length - 1];
        
        // Extend the week range to include the weekend (until next Tuesday)
        const extendedEnd = new Date(lastDate);
        extendedEnd.setDate(extendedEnd.getDate() + 4); // Friday + 4 = Tuesday
        
        // Check if today falls within this week
        if (today >= firstDate && today <= extendedEnd) {
            currentWeekNumber = group.weekNumber;
            
            // Mark all rows in this week
            group.rows.forEach(row => {
                row.setAttribute('data-current-week', 'true');
            });
            return;
        }
        
        // Track the closest week for fallback
        const weekStart = firstDate.getTime();
        const todayTime = today.getTime();
        const diff = Math.abs(todayTime - weekStart);
        
        if (diff < minDiff) {
            minDiff = diff;
            currentWeekNumber = group.weekNumber;
            fallbackWeekRows = group.rows;
        }
    });
    
    // If no week was found within range, use the closest week as fallback
    if (!document.querySelector('[data-current-week="true"]') && fallbackWeekRows) {
        fallbackWeekRows.forEach(row => {
            row.setAttribute('data-current-week', 'true');
        });
    }
}

/**
 * Highlight current week
 */
function initCurrentWeekHighlighting() {
    // Remove any existing indicators first
    document.querySelectorAll('.current-week-indicator').forEach(el => el.remove());
    
    // Find all rows marked as current week
    const currentWeekRows = document.querySelectorAll('[data-current-week="true"]');
    if (currentWeekRows.length > 0) {
        // Find the week cell among these rows (it should be in the first row of the group)
        let weekCell = null;
        for (const row of currentWeekRows) {
            weekCell = row.querySelector('.week-number[rowspan]');
            if (weekCell) break;
        }
        
        // Add "Current Week" indicator to the week cell
        if (weekCell && !weekCell.querySelector('.current-week-indicator')) {
            const indicator = document.createElement('div');
            indicator.className = 'current-week-indicator';
            indicator.innerHTML = '<small style="color: var(--md-accent-fg-color); font-weight: bold;">CURRENT</small>';
            weekCell.appendChild(indicator);
        }
    }
}

/**
 * Initialize smooth navigation for anchor links
 */
function initSmoothNavigation() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const targetId = href.substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL without jumping
                history.pushState(null, null, href);
            }
        });
    });
}

// Add CSS for enhanced interactions
const style = document.createElement('style');
style.textContent = `
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.highlighted {
    background-color: rgba(253, 187, 48, 0.3) !important;
    transition: background-color 0.5s ease;
}

.current-week-indicator {
    text-align: center;
    margin-top: 0.25rem;
}
`;
document.head.appendChild(style);