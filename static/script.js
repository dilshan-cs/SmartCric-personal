// Match State
// let matchData = {
//     teamName: 'Team-Name',
//     totalRuns: 0,
//     wickets: 0,
//     overs: 0.0,
//     batsmen: [
//         { name: 'Batsman-1-', runs: 0, balls: 0, fours: 0, sixes: 0, isStriker: true },
//         { name: 'Batsman-2-', runs: 0, balls: 0, fours: 0, sixes: 0, isStriker: false }
//     ],
//     bowler: [{ name: 'Bowler', runs: 0, overs: 0, wickets: 0 }],
//     currentOver: [],
//     runRate: "0.00",
//     projectedScore: "--",
//     remainingRuns: 0,
//     remainingBalls: 0,
//     rrr: "0.00"
// };
let matchData = {};
let inning1Data = {};
let inning2Data = {};
let currentInning = 1;

// const syncChannel = new BroadcastChannel('cricket_scoring_sync');

// syncChannel.onmessage = (event) => {
//     if (event.data.type === 'REQUEST_DATA') {
//         broadcastUpdate();
//     }
// };

// function broadcastUpdate() {
//     syncChannel.postMessage({
//         type: 'UPDATE_DATA',
//         matchData: matchData,
//         currentInning: currentInning
//     });
// } 

const totalRunsAndWicketEl = document.getElementById('team-score');
const oversEl = document.getElementById('overs');

// Batsman Section 
//batsman 1 
const batsman1CardEl = document.getElementById('batsman-1-card');
const batsman1NameEl = document.getElementById('batsman-1-name');
const batsman1RunsEl = document.getElementById('batsman-1-score');
const batsman1BallsEl = document.getElementById('batsman-1-balls');
const batsman1FoursEl = document.getElementById('batsman-1-fours');
const batsman1SixesEl = document.getElementById('batsman-1-sixes');
const batsman1SrEl = document.getElementById('batsman-1-sr');
const batsman1StrikerIndicatorEl = document.getElementById('batsman-1-striker-indicator');

//batsman 2 
const batsman2CardEl = document.getElementById('batsman-2-card');
const batsman2NameEl = document.getElementById('batsman-2-name');
const batsman2RunsEl = document.getElementById('batsman-2-score');
const batsman2BallsEl = document.getElementById('batsman-2-balls');
const batsman2FoursEl = document.getElementById('batsman-2-fours');
const batsman2SixesEl = document.getElementById('batsman-2-sixes');
const batsman2SrEl = document.getElementById('batsman-2-sr');
const batsman2StrikerIndicatorEl = document.getElementById('batsman-2-striker-indicator');

// Bowler Section 
const bowlerNameEl = document.getElementById('bowler-id');
const bowlerRunsEl = document.getElementById('bowler-score');
const bowlerOversEl = document.getElementById('bowler-overs');
const bowlerWicketsEl = document.getElementById('bowler-wickets');
const bowlerEconomyEl = document.getElementById('bowler-economy');

// Over Section
const currentOverRunsEl = document.getElementById('current-over-runs');


// Run Rate and Required Run Rate Section
const runRateEl = document.getElementById('run-rate');
const requiredRunRateEl = document.getElementById('required-run-rate');
const rrrEl = document.getElementById('rrr');

// Win Prediction Section
const winPredictionEl = document.getElementById('win-prediction');
const winProbabilityEl = document.getElementById('win-probability');


// Remaining Runs and Balls Section
const remainingRunsEl = document.getElementById('remaining-runs');
const remainingBallsEl = document.getElementById('remaining-balls');
const projectedScoreEl = document.getElementById('projected-score');



async function init() {
    try {
        const response = await fetch('/getMatch');
        const data = await response.json();
        // console.log(data);
        // let matchData;
        // let currentInning;
        if (data && data.matchData && Object.keys(data.matchData).length > 0) {
            matchData = data.matchData;
            currentInning = data.currentInning || 1;
            inning1Data = data.inning1Data;
            inning2Data = data.inning2Data;

            const matchIdEl = document.getElementById('match-id-display');
            if (matchIdEl) matchIdEl.textContent = data.match_id || 'N/A';

            updateDisplay(matchData, currentInning, inning1Data, inning2Data);
        }
    }
    catch (error) {
        console.error('Error initializing match data', error)
    }
}


init();




//broadcast channel
const syncChannel = new BroadcastChannel('cricket_scoring_sync');
syncChannel.onmessage = (event) => {
    if (event.data.type === 'REQUEST_DATA') {
        broadcastUpdate();
    }
};

function broadcastUpdate() {
    syncChannel.postMessage({
        type: 'UPDATE_DATA',
        matchData: matchData,
        currentInning: currentInning
    })
}


// async function init() {
//     try {
//         const response = await fetch('/getMatch');
//         const data = await response.json();
//         if (data && data.matchData && data.matchData.totalRuns !== undefined) {
//             matchData = data.matchData;
//             currentInning = data.currentInning || 1;
//             updateDisplay();
//         }
//     } catch (error) {
//         console.error('Error initializing match data:', error);
//     }
// }




// async function syncWithBackend() {
//     try {
//         await fetch('/syncSession', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({
//                 matchData: matchData,
//                 currentInning: currentInning
//             })
//         });
//     } catch (error) {
//         console.error('Error syncing with backend:', error);
//     }
// }

// async function syncWithBackend() {
//     try {
//         await fetch('/syncSession', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 matchData: matchData,
//                 currentInning: currentInning
//             })
//         });
//     } catch (error) {
//         console.log('Error syncing data backend', error)
//     }

// }



//////////////////////////////////////////////////////////////////////////////////
function updateDisplay(matchData, currentInning, inning1Data, inning2Data) {
    const totalRuns = matchData.totalRuns || 0;
    const wickets = matchData.wickets || 0;
    const overs = matchData.overs || 0.0;
    const batsmen = matchData.batsmen;
    const bowler = matchData.bowler;

    // ... existing UI updates ... 
    console.log(currentInning);
    // const scoreEl = document.getElementById('team-score');
    if (totalRunsAndWicketEl) {
        totalRunsAndWicketEl.textContent = `${totalRuns}/${wickets}`;
    }
    if (currentInning === 1) {
        const inningBadge = document.getElementById('inning-badge');
        if (inningBadge) inningBadge.textContent = 'Inning 1';
    } else {
        const inningBadge = document.getElementById('inning-badge');
        if (inningBadge) inningBadge.textContent = 'Inning 2';
    }

    if (batsmen) {
        batsmen.forEach((b, i) => {
            const idx = i + 1;
            const nameEl = document.getElementById(`batsman-${idx}-name`);
            const scoreEl = document.getElementById(`batsman-${idx}-score`);
            const ballsEl = document.getElementById(`batsman-${idx}-ball`);
            const foursEl = document.getElementById(`batsman-${idx}-fours`);
            const sixesEl = document.getElementById(`batsman-${idx}-sixes`);
            const srEl = document.getElementById(`batsman-${idx}-sr`);
            const cardEl = document.getElementById(`batsman-${idx}-card`);

            if (nameEl) nameEl.textContent = b.name;
            if (scoreEl) scoreEl.textContent = b.runs;
            if (ballsEl) ballsEl.textContent = b.balls;
            if (foursEl) foursEl.textContent = b.fours;
            if (sixesEl) sixesEl.textContent = b.sixes;
            if (srEl) {
                const sr = b.balls > 0 ? ((b.runs / b.balls) * 100).toFixed(2) : '0.00';
                srEl.textContent = sr;
            }

            // Highlight active striker
            if (cardEl) {
                cardEl.className = b.isStriker ? 'batsman-card-active' : 'batsman-card';
            }

            const dotEl = document.getElementById(`striker-indicator${idx}`);
            if (dotEl) {
                dotEl.style.display = b.isStriker ? 'inline' : 'none';
            }
        });
    }

    if (bowler) {
        const currentBowler = Array.isArray(bowler) ? bowler[0] : bowler;
        if (currentBowler) {
            if (bowlerNameEl) bowlerNameEl.textContent = currentBowler.name || '';
            if (bowlerRunsEl) {
                const w = currentBowler.wickets || 0;
                const r = currentBowler.runs || 0;
                bowlerRunsEl.textContent = `${w}-${r}`;
            }
            if (bowlerOversEl) bowlerOversEl.textContent = currentBowler.overs || 0;
            if (bowlerEconomyEl) {
                const bOvers = currentBowler.overs || 0;
                const bWhole = Math.floor(bOvers);
                const bBalls = Math.round((bOvers % 1) * 10);
                const bTotalBalls = (bWhole * 6) + bBalls;
                const eco = bTotalBalls > 0 ? ((currentBowler.runs || 0) / (bTotalBalls / 6)).toFixed(2) : '0.00';
                bowlerEconomyEl.textContent = eco;
            }
        }
    }

    // Update Overs
    const teamOversEl = document.getElementById('team-overs');
    if (teamOversEl) {
        teamOversEl.textContent = Number(overs).toFixed(1);
    }

    // Update Run Rate
    const totalBalls = Math.floor(overs) * 6 + Math.round((overs % 1) * 10);
    const rr = totalBalls > 0 ? (totalRuns / (totalBalls / 6)).toFixed(2) : '0.00';
    matchData.runRate = rr;

    const rrEl = document.getElementById('current-run-rate');
    if (rrEl) {
        rrEl.textContent = rr;
    }

    // Update Projected Score
    const totalOvers = matchData.totalOvers || 20;
    const projectedScore = totalBalls > 0 ? Math.round((totalRuns / totalBalls) * (totalOvers * 6)) : 0;
    const projectedEl = document.getElementById('projected-score');
    if (projectedEl) {
        projectedEl.textContent = projectedScore;
        const projectedLabelEl = document.getElementById('projected-score-label');
        if (projectedLabelEl) projectedLabelEl.textContent = `At ${rr} RR`;
    }

    // Update This Over
    const thisOverEl = document.getElementById('this-over-content');
    if (thisOverEl) {
        if (matchData.currentOver && matchData.currentOver.length > 0) {
            thisOverEl.innerHTML = '';
            matchData.currentOver.forEach(ball => {
                const ballEl = document.createElement('span');
                ballEl.className = 'ball';

                // Add specific class based on value
                if (ball === 'W') {
                    ballEl.classList.add('ball-W');
                } else if (typeof ball === 'number') {
                    ballEl.classList.add(`ball-${ball}`);
                } else if (typeof ball === 'string' && ball.includes('w')) {
                    ballEl.classList.add('ball-w');
                } else if (typeof ball === 'string' && ball.includes('nb')) {
                    ballEl.classList.add('ball-nb');
                }

                ballEl.textContent = ball;
                thisOverEl.appendChild(ballEl);
            });
        } else {
            thisOverEl.textContent = 'No balls this over yet';
        }
    }

    // Update Commentary
    const commentaryEl = document.getElementById('commentary-card-list');
    if (commentaryEl) {
        commentaryEl.innerHTML = '';
        if (matchData.commentary) {
            matchData.commentary.forEach(text => {
                const item = document.createElement('div');
                item.className = 'commentary-item';
                item.textContent = text;
                if (text.includes('WICKET')) item.classList.add('commentary-wicket');
                commentaryEl.appendChild(item);
            });
        }
    }

    // Update Fall of Wickets
    const fowEl = document.getElementById('fow-list');
    if (fowEl) {
        fowEl.innerHTML = '';
        if (matchData.fallOfWickets) {
            matchData.fallOfWickets.forEach(fow => {
                const item = document.createElement('div');
                item.className = 'fow-item';
                item.innerHTML = `
                    <div class="fow-wickets">${fow.wicket_num}-${fow.runs}</div>
                    <div class="fow-overs">(${fow.overs})</div>
                `;
                fowEl.appendChild(item);
            });
        }
    }

    // Check for new bowler modal
    if (overs > 0 && overs % 1 === 0 && !matchData.isOverChanging) {
        // Only show if wickets < 10 and overs < totalOvers
        if (wickets < 10 && (matchData.totalOvers === 0 || overs < matchData.totalOvers)) {
            onNewBowlerClick();
        }
    }

    // --- Inning Termination & Requirement Logic ---
    const requirementSection = document.getElementById('requirement__section');
    if (currentInning === 1) {
        if (requirementSection) requirementSection.style.display = 'none';

        // Check for Inning 1 termination
        if (wickets >= 10 || (matchData.totalOvers > 0 && overs >= matchData.totalOvers)) {
            const modal = document.getElementById('second-inning-modal');
            if (modal) modal.classList.add('show');
        }
    } else {
        // Inning 2 Logic
        if (requirementSection) requirementSection.style.display = 'block';

        const target = (inning1Data ? inning1Data.totalRuns : 0) + 1;
        const runsNeeded = target - totalRuns;
        const totalBallsToBowl = (matchData.totalOvers || 0) * 6;
        const ballsRemaining = totalBallsToBowl - totalBalls;

        // Update Requirement Section
        const reqRunsVal = document.querySelector('.requirement__runs-value');
        const reqBallsVal = document.querySelector('.requirement__balls-value');
        const reqRRVal = document.getElementById('requirement-run-rate');

        if (reqRunsVal) reqRunsVal.textContent = Math.max(0, runsNeeded);
        if (reqBallsVal) reqBallsVal.textContent = Math.max(0, ballsRemaining);
        if (reqRRVal) {
            const rrr = ballsRemaining > 0 ? ((runsNeeded / (ballsRemaining / 6))).toFixed(2) : "0.00";
            reqRRVal.textContent = `Required Run Rate: ${rrr}`;
        }

        // Check for Match Result
        // 1. Team 2 wins
        if (totalRuns >= target) {
            showResultModal(inning1Data, inning2Data);
        }
        // 2. Team 2 loses (All out or Overs completed)
        else if (wickets >= 10 || (matchData.totalOvers > 0 && overs >= matchData.totalOvers)) {
            showResultModal(inning1Data, inning2Data);
        }
    }

    // Sync with local windows and backend
    broadcastUpdate();
}


async function addRuns(runs) {
    // matchData.totalRuns += runs;
    fetch('/addRuns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ runs })
    });

    const response = await fetch('/getMatch');
    const data = await response.json();
    console.log(data);

    matchData = data.matchData;
    currentInning = data.currentInning;
    inning1Data = data.inning1Data;
    inning2Data = data.inning2Data;

    updateDisplay(matchData, currentInning, inning1Data, inning2Data);
    // Increment balls/overs (assuming every run button click is a legal ball for now)
    // incrementOvers();

    ////////////////////////////////////////////////////////////////////////////////


    // Update current over list for scoreboard
    // matchData.currentOver.push(runs);
    // if (matchData.currentOver.length > 6) {
    //     matchData.currentOver = [runs]; // Reset on new over (simplified)
    // }

    ////////////////////////////////////////////////////////////////////////////////

    // Update Striker runs (basic implementation)
    // const striker = matchData.batsmen.find(b => b.isStriker);
    // if (striker) {
    //     striker.runs += runs;
    //     striker.balls += 1;
    //     if (runs === 4) striker.fours += 1;
    //     if (runs === 6) striker.sixes += 1;
    // }

    ////////////////////////////////////////////////////////////////////////////////



    // Update Bowler stats
    // if (matchData.bowler && matchData.bowler[0]) {
    //     const b = matchData.bowler[0];
    //     b.runs += runs;
    //     // Increment bowler balls
    //     let whole = Math.floor(b.overs);
    //     let balls = Math.round((b.overs - whole) * 10);
    //     balls += 1;
    //     if (balls >= 6) {
    //         whole += 1;
    //         balls = 0;
    //     }
    //     b.overs = parseFloat(`${whole}.${balls}`);
    // }

    ////////////////////////////////////////////////////////////////////////////////


    // Swap striker on odd runs
    // if (runs === 1 || runs === 3 || runs === 5) {
    //     matchData.batsmen.forEach(b => b.isStriker = !b.isStriker);
    // }

}

async function setStriker(index) {
    const response = await fetch('/setStriker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index })
    });
    const data = await response.json();
    matchData = data.data.matchData;
    currentInning = data.data.currentInning;
    inning1Data = data.data.inning1Data;
    inning2Data = data.data.inning2Data;
    updateDisplay(matchData, currentInning, inning1Data, inning2Data);
}

function openPopOutScoreboard() {
    window.open('/scoreboard', 'Cricket Scoreboard', 'width=1000,height=1000,scrollbars=yes');
}

// Expose functions to global scope for HTML onclick handlers
// Object.assign(window, {
//     addRuns,
//     setStriker,
//     openPopOutScoreboard,
//     // Placeholder for other functions to avoid immediate errors
//     showMatchOverview: () => console.log('Match Overview clicked'),
//     onNewPlayersClick: () => console.log('New Players clicked'),
//     onNewMatchClick: () => console.log('New Match clicked'),
//     swapCurrentInning: () => console.log('Swap Inning clicked'),
//     onNewBowlerClick: () => console.log('New Bowler clicked'),
// });

async function resetMatch() {
    const response = await fetch('/newMatch', { method: 'POST' });
    const data = await response.json();
    matchData = data.data.matchData;
    currentInning = data.data.currentInning;
    inning1Data = data.data.inning1Data;
    inning2Data = data.data.inning2Data;

    const matchIdEl = document.getElementById('match-id-display');
    if (matchIdEl) matchIdEl.textContent = data.match_id || 'N/A';

    updateDisplay(matchData, currentInning, inning1Data, inning2Data);
    const modal = document.getElementById('new-match-modal');
    if (modal) modal.classList.remove('show');
}

function onNewMatchClick() {
    const modal = document.getElementById('new-match-modal');
    if (modal) modal.classList.add('show');
}

function doNothing() {
    const modal = document.getElementById('new-match-modal');
    if (modal) modal.classList.remove('show');
}

function onNewPlayersClick() {
    const modal = document.getElementById('new-players-modal');
    if (modal) modal.classList.add('show');
}

async function handleNewPlayer() {
    const selectedInning = document.querySelector('input[name="inning-radio"]:checked')?.value || "1";
    const inning = parseInt(selectedInning, 10);

    const tournementName = document.getElementById('tournement-name-input')?.value.trim();
    const teamName = document.getElementById('team-name-input')?.value.trim();
    const totalOvers = parseInt(document.getElementById('total-overs-input')?.value.trim()) || 0;

    const b1 = document.getElementById('batsman-input-1-')?.value.trim() || 'Batsman-1-';
    const b2 = document.getElementById('batsman-input-2-')?.value.trim() || 'Batsman-2-';

    const batsmen = [
        { name: b1, runs: 0, balls: 0, fours: 0, sixes: 0, isStriker: true },
        { name: b2, runs: 0, balls: 0, fours: 0, sixes: 0, isStriker: false }
    ];

    const availableBatsmen = [];
    for (let i = 3; i <= 11; i++) {
        const bn = document.getElementById(`batsman-input-${i}-`)?.value.trim();
        if (bn) availableBatsmen.push(bn);
    }

    const response = await fetch('/setPlayers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inning,
            tournementName,
            teamName,
            totalOvers,
            batsmen,
            availableBatsmen
        })
    });

    const data = await response.json();
    matchData = data.data.matchData;
    currentInning = data.data.currentInning;
    inning1Data = data.data.inning1Data;
    inning2Data = data.data.inning2Data;
    updateDisplay(matchData, currentInning, inning1Data, inning2Data);

    const modal = document.getElementById('new-players-modal');
    if (modal) modal.classList.remove('show');

    showPlayersStoredConfirmation(inning);
}

function showPlayersStoredConfirmation(inningNumber) {
    const confirmationOverlay = document.getElementById("confirmation-players-stored");
    const message = document.getElementById("success-message");

    if (!confirmationOverlay) return;

    if (message) {
        message.textContent = `Inning ${inningNumber} Data Stored Successfully`;
    }

    confirmationOverlay.classList.add("show");

    // Trigger animation in next frame
    requestAnimationFrame(() => {
        confirmationOverlay.classList.add("is-visible");
    });

    setTimeout(() => {
        confirmationOverlay.classList.remove("is-visible");

        // Wait for opacity transition before hiding entirely
        setTimeout(() => {
            confirmationOverlay.classList.remove("show");
        }, 300);
    }, 2600);
}

function doNothing2() {
    const modal = document.getElementById('new-players-modal');
    if (modal) modal.classList.remove('show');
}

function clearNewPlayerInputs() {
    const inputs = document.querySelectorAll('#new-players-modal .modal-input');
    inputs.forEach(input => input.value = '');
}

async function showMatchOverview() {
    const response = await fetch('/matchOverview');
    const data = await response.json();

    const i1 = data.inning1Data;
    const i2 = data.inning2Data;

    // Inning 1
    const team1El = document.getElementById('team-1');
    if (team1El) team1El.textContent = i1.teamName;
    const i1RunsEl = document.getElementById('inning-1-total-run');
    if (i1RunsEl) i1RunsEl.textContent = `Score: ${i1.totalRuns}/${i1.wickets} in ${i1.overs} Overs`;
    const i1ExtrasEl = document.getElementById('inning-1-extraRuns');
    if (i1ExtrasEl) i1ExtrasEl.textContent = i1.extraRuns || 0;

    renderBatsmenTable('inning-1-batsmen-table', i1);
    renderBowlersTable('inning-1-bowlers-table', i1);

    // Inning 2
    const team2El = document.getElementById('team-2');
    if (team2El) team2El.textContent = i2.teamName;
    const i2RunsEl = document.getElementById('inning-2-total-run');
    if (i2RunsEl) i2RunsEl.textContent = `Score: ${i2.totalRuns}/${i2.wickets} in ${i2.overs} Overs`;
    const i2ExtrasEl = document.getElementById('inning-2-extraRuns');
    if (i2ExtrasEl) i2ExtrasEl.textContent = i2.extraRuns || 0;

    renderBatsmenTable('inning-2-batsmen-table', i2);
    renderBowlersTable('inning-2-bowlers-table', i2);

    const modal = document.getElementById('match-overview-modal');
    if (modal) modal.classList.add('show');
}

function calStrikeRate(runs, balls) {
    return balls > 0 ? ((runs / balls) * 100).toFixed(2) : '0.00';
}

function renderBatsmenTable(containerId, inningData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Prepare combined list with isOut property
    const dismissed = (inningData.dismissedBatsmen || []).map(b => ({ ...b, isOut: true }));
    const current = (inningData.batsmen || []).map(b => ({ ...b, isOut: false }));
    const allBatsmen = [...dismissed, ...current].filter(b => b.name && !b.name.startsWith('Batsman-'));

    // container.innerHTML = ` 
    //     <table>
    //         <tr class="section-label">
    //             <th>Batsman</th>
    //             <th>R</th>
    //             <th>B</th>
    //             <th>4s</th>
    //             <th>6s</th>
    //             <th>SR</th>
    //         </tr>
    //         ${allBatsmen.map(b => `
    //             <tr>
    //                 ${b.isOut ? `<td>${b.name}</td>` : `<td>${b.name}*</td>`}
    //                 <td>${b.runs}</td>
    //                 <td>${b.balls}</td>
    //                 <td>${b.fours}</td>
    //                 <td>${b.sixes}</td>
    //                 <td>${calStrikeRate(b.runs, b.balls)}</td>
    //             </tr>
    //         `).join('')}
    //     </table>
    // `; 

    container.innerHTML = `
        <table>
            <tr class = 'section-label'>
                <th>Batsman</th>
                <th>R</th>
                <th>B</th>
                <th>4s</th>
                <th>6s</th>
                <th>SR</th>
            </tr>
            ${allBatsmen.map(b => `
                <tr>
                    ${b.isOut ? `<td>${b.name}</td>` : `<td>${b.name}*</td>`}
                    <td>${b.runs}</td>
                    <td>${b.balls}</td>
                    <td>${b.fours}</td>
                    <td>${b.sixes}</td>
                    <td>${calStrikeRate(b.runs, b.balls)}</td>
                </tr>
                `).join()}
        </table>
    `;

}

function renderBowlersTable(containerId, inningData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Combine past and current bowlers
    const pastBowlers = (inningData.pastOver || []).map(arr => arr[0]);
    const currentBowler = inningData.bowler[0];
    const allBowlers = [...pastBowlers];

    if (currentBowler && currentBowler.name && !currentBowler.name.startsWith('Bowler')) {
        const alreadyAdded = allBowlers.some(b => b.name === currentBowler.name);
        if (!alreadyAdded) allBowlers.push(currentBowler);
    }

    container.innerHTML = `
        <table>
            <tr class="section-label">
                <th>Bowler</th>
                <th>O</th>
                <th>R</th>
                <th>W</th>
                <th>E</th>
            </tr>
            ${allBowlers.map(b => {
        const bWhole = Math.floor(b.overs);
        const bBalls = Math.round((b.overs - bWhole) * 10);
        const bTotalBalls = (bWhole * 6) + bBalls;
        const economy = bTotalBalls > 0 ? (b.runs / (bTotalBalls / 6)).toFixed(2) : '0.00';
        return `
                    <tr>
                        <td>${b.name}</td>
                        <td>${b.overs}</td>
                        <td>${b.runs}</td>
                        <td>${b.wickets}</td>
                        <td>${economy}</td>
                    </tr>
                `;
    }).join('')}
        </table>
    `;
}

function closeMatchOverviewModal() {
    const modal = document.getElementById('match-overview-modal');
    if (modal) modal.classList.remove('show');
}

async function swapCurrentInning() {
    const response = await fetch('/swapInning', { method: 'POST' });
    const data = await response.json();
    matchData = data.data.matchData;
    currentInning = data.data.currentInning;
    inning1Data = data.data.inning1Data;
    inning2Data = data.data.inning2Data;

    const m1 = document.getElementById('second-inning-modal');
    if (m1) m1.classList.remove('show');

    const m2 = document.getElementById('new-inning-modal');
    if (m2) m2.classList.remove('show');

    updateDisplay(matchData, currentInning, inning1Data, inning2Data);
}

function doNothing4() {
    const modal = document.getElementById('new-inning-modal');
    if (modal) modal.classList.remove('show');
}

function doNothing5() {
    const modal = document.getElementById('second-inning-modal');
    if (modal) modal.classList.remove('show');
}

async function generateDocx() {
    const element = document.getElementById('match-report-template');
    if (!element) return;

    element.style.display = 'block';

    // Populate data
    const reportDate = document.getElementById('report-date');
    if (reportDate) reportDate.textContent = new Date().toLocaleString();

    const reportResultText = document.getElementById('report-result-text');
    const resultMessage = document.getElementById('result-message');
    if (reportResultText && resultMessage) {
        reportResultText.textContent = resultMessage.textContent || "Match in progress";
    }

    // Fetch latest overview data
    const response = await fetch('/matchOverview');
    const data = await response.json();
    const i1 = data.inning1Data;
    const i2 = data.inning2Data;

    // Inning 1 Teams & Scores
    const i1Team = document.getElementById('report-i1-team');
    if (i1Team) i1Team.textContent = i1.teamName || 'Team 1';
    const i1Score = document.getElementById('report-i1-score');
    if (i1Score) i1Score.textContent = `${i1.totalRuns}/${i1.wickets} (${i1.overs} ov)`;
    const i1Extras = document.getElementById('report-i1-Extra-Runs');
    if (i1Extras) i1Extras.textContent = i1.extraRuns || 0;

    // Inning 2 Teams & Scores
    const i2Team = document.getElementById('report-i2-team');
    if (i2Team) i2Team.textContent = i2.teamName || 'Team 2';
    const i2Score = document.getElementById('report-i2-score');
    if (i2Score) i2Score.textContent = `${i2.totalRuns}/${i2.wickets} (${i2.overs} ov)`;
    const i2Extras = document.getElementById('report-i2-Extra-Runs');
    if (i2Extras) i2Extras.textContent = i2.extraRuns || 0;

    // Bowler Team Names & Scores (Opposite team bowls)
    const i2TeamBowler = document.getElementById('report-i2-team-bowler');
    if (i2TeamBowler) i2TeamBowler.textContent = i2.teamName || 'Team 2';
    const i1BowlerScore = document.getElementById('report-i1-bowler-score');
    if (i1BowlerScore) i1BowlerScore.textContent = `${i1.totalRuns}/${i1.wickets} (${i1.overs} ov)`;

    const i1TeamBowler = document.getElementById('report-i1-team-bowler');
    if (i1TeamBowler) i1TeamBowler.textContent = i1.teamName || 'Team 1';
    const i2BowlerScore = document.getElementById('report-i2-bowler-score');
    if (i2BowlerScore) i2BowlerScore.textContent = `${i2.totalRuns}/${i2.wickets} (${i2.overs} ov)`;

    // Tables 
    renderBatsmenTable('report-i1-batsmen', i1);
    renderBatsmenTable('report-i2-batsmen', i2);
    renderBowlersTable('report-i1-bowlers-table', i1);
    renderBowlersTable('report-i2-bowlers-table', i2);

    // Commentary
    const comm1 = document.getElementById('report-commentary-1');
    if (comm1) comm1.innerHTML = (i1.commentary || []).map(c => `<p>${c}</p>`).join('');
    const comm2 = document.getElementById('report-commentary-2');
    if (comm2) comm2.innerHTML = (i2.commentary || []).map(c => `<p>${c}</p>`).join('');

    const filename = `Match_Report_${i1.teamName || 'Team1'}_vs_${i2.teamName || 'Team2'}.docx`;

    const styles = `
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            h1 { color: #2c3e50; text-align: center; }
            h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
            h3 { color: #2980b9; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .highlight-result { font-weight: bold; color: #e74c3c; font-size: 1.2em; }
            .report-score { font-weight: bold; margin-bottom: 10px; }
            .report-inning { margin-bottom: 20px; }
        </style>
    `;

    const htmlContent = `
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <title>Match Report</title>
                ${styles}
            </head>
            <body>
                <div class="report-container">
                    ${element.innerHTML}
                </div>
            </body>
        </html>
    `;

    const converted = htmlDocx.asBlob(htmlContent);
    saveAs(converted, filename);

    setTimeout(() => {
        element.style.display = 'none';
    }, 1000);
}


Object.assign(window, {
    addRuns,
    setStriker,
    openPopOutScoreboard,
    resetMatch,
    onNewMatchClick,
    doNothing,
    onNewPlayersClick,
    handleNewPlayer,
    doNothing2,
    clearNewPlayerInputs,
    showMatchOverview,
    closeMatchOverviewModal,
    swapCurrentInning,
    doNothing4,
    doNothing5,
    onNewBowlerClick,
    confirmNewBowler,
    doNothingBowler,
    fallWickets,
    confirmNewBatsman,
    doNothing3,
    addCustomRuns,
    addCustomExtra,
    handleUndo,
    closeResultModal,
    generateDocx
});

function showResultModal(inning1Data, inning2Data) {
    const modal = document.getElementById('result-modal');
    const messageEl = document.getElementById('result-message');
    if (!modal || !messageEl) return;

    const i1Runs = inning1Data.totalRuns;
    const i2Runs = inning2Data.totalRuns;
    const i2Wickets = inning2Data.wickets;
    const i1Team = inning1Data.teamName || 'Team 1';
    const i2Team = inning2Data.teamName || 'Team 2';

    let result = "";
    if (i2Runs > i1Runs) {
        result = `${i2Team} won by ${10 - i2Wickets} wickets`;
    } else if (i2Runs < i1Runs) {
        result = `${i1Team} won by ${i1Runs - i2Runs} runs`;
    } else {
        result = "Match Tied";
    }

    messageEl.textContent = result;
    modal.classList.add('show');
}

function closeResultModal() {
    const modal = document.getElementById('result-modal');
    if (modal) modal.classList.remove('show');
}

async function handleUndo() {
    const response = await fetch('/undo', { method: 'POST' });
    const data = await response.json();

    if (data.status === 'success') {
        matchData = data.data.matchData;
        currentInning = data.data.currentInning;
        inning1Data = data.data.inning1Data;
        inning2Data = data.data.inning2Data;
        updateDisplay(matchData, currentInning, inning1Data, inning2Data);
    } else {
        alert(data.message || 'Undo failed');
    }
}

async function addCustomRuns() {
    const input = document.getElementById('custom-runs-input');
    const runs = parseInt(input.value);
    if (isNaN(runs) || runs < 0) return;

    await addRuns(runs);
    input.value = '';
}

async function addCustomExtra() {
    const type = document.getElementById('custom-extra-type').value;
    const runsInput = document.getElementById('custom-extra-runs-input');
    const runs = parseInt(runsInput.value) || 0;
    const isByeOnNb = document.getElementById('bye-runs-for-noball')?.checked || false;

    const response = await fetch('/addExtra', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            extra_type: type,
            runs: runs,
            is_bye_on_nb: isByeOnNb
        })
    });

    const data = await response.json();
    matchData = data.data.matchData;
    currentInning = data.data.currentInning;
    inning1Data = data.data.inning1Data;
    inning2Data = data.data.inning2Data;
    updateDisplay(matchData, currentInning, inning1Data, inning2Data);

    runsInput.value = '';
}

async function fallWickets(type = 'bowled') {
    const runsOnWicket = parseInt(document.getElementById('custom-runs-input-runout')?.value) || 0;
    const isInvalid = document.getElementById('invalid-ball-radio')?.checked || false;
    const isByeOnNb = document.getElementById('bye-runs-for-noball')?.checked || false;

    const response = await fetch('/addWicket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            wicket_type: type,
            runs: runsOnWicket,
            is_invalid: isInvalid,
            is_bye_on_nb: isByeOnNb
        })
    });
    const data = await response.json();
    matchData = data.data.matchData;
    currentInning = data.data.currentInning;
    inning1Data = data.data.inning1Data;
    inning2Data = data.data.inning2Data;
    updateDisplay(matchData, currentInning, inning1Data, inning2Data);

    if (matchData.wickets < 10) {
        showNewBatsmanModal();
    }
}

function showNewBatsmanModal() {
    const list = document.getElementById('batsman-options-list');
    list.innerHTML = '';

    if (matchData.availableBatsmen && matchData.availableBatsmen.length > 0) {
        matchData.availableBatsmen.forEach(pName => {
            const btn = document.createElement('button');
            btn.className = 'batsman-option-btn';
            btn.textContent = pName;
            btn.onclick = () => confirmNewBatsman(pName);
            list.appendChild(btn);
        });
    } else {
        list.innerHTML = '<p style="color:#aaa; text-align:center;"> No more batsmen available </p>';
    }

    const modal = document.getElementById('new-batsman-modal');
    if (modal) modal.classList.add('show');
}

async function confirmNewBatsman(name) {
    const response = await fetch('/setNewBatsman', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batsmanName: name })
    });
    const data = await response.json();
    matchData = data.data.matchData;
    currentInning = data.data.currentInning;
    inning1Data = data.data.inning1Data;
    inning2Data = data.data.inning2Data;
    updateDisplay(matchData, currentInning, inning1Data, inning2Data);

    const modal = document.getElementById('new-batsman-modal');
    if (modal) modal.classList.remove('show');
}

function doNothing3() {
    const modal = document.getElementById('new-batsman-modal');
    if (modal) modal.classList.remove('show');
}

async function onNewBowlerClick() {
    const response = await fetch('/getMatch');
    const data = await response.json();

    const oppositeInningData = data.currentInning === 1 ? data.inning2Data : data.inning1Data;

    const allPlayers = new Set();

    if (oppositeInningData.batsmen) {
        oppositeInningData.batsmen.forEach(b => {
            if (b.name && !b.name.startsWith('Batsman-')) allPlayers.add(b.name);
        });
    }
    if (oppositeInningData.availableBatsmen) {
        oppositeInningData.availableBatsmen.forEach(b => {
            if (b && !b.startsWith('Batsman-')) allPlayers.add(b);
        });
    }

    const list = document.getElementById('bowler-options-list');
    list.innerHTML = '';

    if (allPlayers.size === 0) {
        list.innerHTML = '<p style="color:#aaa; text-align:center;"> No players available in opposite team </p>';
    } else {
        Array.from(allPlayers).forEach(pName => {
            const btn = document.createElement('button');
            btn.className = 'batsman-option-btn';
            btn.textContent = pName;
            btn.onclick = () => confirmNewBowler(pName);
            list.appendChild(btn);
        });
    }

    // const modal = document.getElementById('new-bowler-modal');
    // if (modal) modal.classList.add('show');
}

async function confirmNewBowler(name) {
    const response = await fetch('/setBowler', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bowlerName: name })
    });
    const data = await response.json();
    matchData = data.data.matchData;
    currentInning = data.data.currentInning;
    inning1Data = data.data.inning1Data;
    inning2Data = data.data.inning2Data;
    updateDisplay(matchData, currentInning, inning1Data, inning2Data);

    const modal = document.getElementById('new-bowler-modal');
    if (modal) modal.classList.remove('show');
}

function doNothingBowler() {
    const modal = document.getElementById('new-bowler-modal');
    if (modal) modal.classList.remove('show');
}


