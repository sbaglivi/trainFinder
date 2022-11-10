"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const python_shell_1 = require("python-shell");
const cors_1 = __importDefault(require("cors"));
const fs_1 = __importDefault(require("fs"));
const app = (0, express_1.default)();
app.use((0, cors_1.default)());
app.use(express_1.default.json());
let trenitaliaResultsMap = new Map();
let italoResultsMap = new Map();
app.get('/', (req, res) => {
    //	res.sendFile(path.join(__dirname, 'index.html'))
    res.send("Hello World");
});
app.get('/try', (req, res) => {
    res.send("Other urls work as well");
});
function logToFile(text) {
    fs_1.default.writeFile(path_1.default.join(__dirname, "log.txt"), text + '\n', { 'flag': 'a' }, err => {
        if (err)
            throw err;
    });
}
function pyrun(script, options) {
    return __awaiter(this, void 0, void 0, function* () {
        return new Promise((resolve, reject) => {
            try {
                fs_1.default.writeFile(path_1.default.join(__dirname, "log.txt"), path_1.default.join(__dirname, script) + '\n', { 'flag': 'a' }, err => {
                    if (err)
                        throw err;
                });
                python_shell_1.PythonShell.run(path_1.default.join(__dirname, script), options, (pyErr, pyResults) => {
                    if (pyErr) {
                        console.log('error while running ' + script);
                        logToFile('Error:' + pyErr);
                        reject(pyErr);
                    }
                    else
                        resolve((pyResults === null || pyResults === void 0 ? void 0 : pyResults.length) > 0 ? pyResults[0] : []);
                });
            }
            catch (e) {
                console.log(e.message);
                reject(e.message);
            }
        });
    });
}
function getTrainResults(script, options, map, mapId) {
    return __awaiter(this, void 0, void 0, function* () {
        let secondsSinceEpoch = getSecondsSinceEpoch();
        if (map.has(mapId) && (secondsSinceEpoch - map.get(mapId).requestTime < 600)) {
            console.log('Found data in cache for ' + script);
            // return {error: null, results: map.get(mapId).data}
            return map.get(mapId).data;
        }
        else {
            try {
                let results = yield pyrun(script, options);
                if (results.length === 0)
                    throw Error('Found no trains on ' + script + ' for desired time\n');
                map.set(mapId, { requestTime: secondsSinceEpoch, data: results });
                // return {error: null, results}
                return results;
            }
            catch (e) {
                console.log(e.message);
                // return {error: e.message, results: []}
                return [];
            }
        }
    });
}
function getSecondsSinceEpoch() {
    let curDate = new Date();
    return Math.floor(curDate.getTime() / 1000);
}
function getScriptOptions(reqBody, type, company) {
    let mode = 'json', args;
    const { origin, destination, dateTime, passengers } = reqBody;
    let [depDate, depTime] = dateTime.split(' ');
    // depDate = depDate.replaceAll('/','-'); typescript error: replaceAll does not exist on type string
    depDate = depDate.split('/').join('-');
    if (type !== 'oneway') {
        const { returnDateTime } = reqBody;
        let [retDate, retTime] = returnDateTime.split(' ');
        retDate = retDate.split('/').join('-');
        if (type === 'outgoing') {
            args = [origin, destination, depDate, depTime, passengers, retDate, retTime];
        }
        else if (type === 'returning') {
            const { cookies } = reqBody;
            if (company === 'trenitalia') {
                const { goingoutId, cartId } = reqBody;
                args = [origin, destination, depDate, depTime, passengers, retDate, retTime, goingoutId, cartId, JSON.stringify(cookies)];
            }
            else {
                const { inputValue } = reqBody;
                args = [origin, destination, depDate, depTime, passengers, retDate, retTime, inputValue, JSON.stringify(cookies)];
            }
        }
    }
    else {
        args = [origin, destination, depDate, depTime, passengers];
    }
    return { mode, args };
}
app.post('/return', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { company } = req.body;
    const { origin, destination, dateTime, returnDateTime, passengers, cookies } = req.body;
    let [date, time] = dateTime.split(' ');
    date = date.replaceAll('/', '-');
    let [returnDate, returnTime] = returnDateTime.split(' ');
    returnDate = returnDate.replaceAll('/', '-');
    let results, scriptName, options;
    if (company === 'italo') {
        const { inputValue } = req.body;
        options = {
            mode: 'json',
            args: [origin, destination, date, time, passengers, returnDate, returnTime, inputValue, JSON.stringify(cookies)]
        };
        scriptName = 'ireturn.py';
        results = yield pyrun('ireturn.py', options);
    }
    else if (company === 'trenitalia') {
        const { cartId, goingoutId } = req.body;
        options = {
            mode: 'json',
            args: [origin, destination, date, time, passengers, returnDate, returnTime, goingoutId, cartId, JSON.stringify(cookies)]
        };
        console.log(options.args);
        scriptName = 'treturn.py';
    }
    try {
        results = yield pyrun(scriptName, options);
        res.json(results);
    }
    catch (e) {
        console.log('While trying to find return trains I encountered an error');
        console.log(e.message);
    }
}));
app.post('/outgoingOnly', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { origin, destination, dateTime, passengers } = req.body;
    let [date, time] = dateTime.split(' ');
    date = date.replaceAll('/', '-');
    let options = {
        mode: "json",
        args: [origin, destination, date, time, passengers]
    };
    let trenitaliaMapId = origin + destination + dateTime;
    let italoMapId = origin + destination + dateTime;
    // 								CHECK SCRIPTS TO RUN
    let trenitaliaResult = getTrainResults('toneway.py', options, trenitaliaResultsMap, trenitaliaMapId);
    let italoResult = getTrainResults('ioneway.py', options, italoResultsMap, italoMapId);
    Promise.all([trenitaliaResult, italoResult])
        .then(results => {
        fs_1.default.writeFile(path_1.default.join(__dirname, "log.txt"), JSON.stringify(results) + '\n', { 'flag': 'a' }, err => {
            if (err)
                throw err;
        });
        res.json({
            error: results[0].error + results[1].error,
            results: [...results[0].results, ...results[1].results]
        });
    })
        .catch(e => {
        console.log('Encountered an error while searching for one way results for both companies');
        console.log(e.message);
    });
    /*
    Promise.all([trenitaliaResult, italoResult]).then(results => {
        let combinedResults = results.reduce((a,b)=> ({error: a.error + b.error, results: [...a.results, ...b.results]}))
        res.json(JSON.stringify(combinedResults));
    })
    */
}));
app.post('/allNoOffers', (req, res) => {
    const { origin, destination, dateTime, returnDateTime, passengers } = req.body;
    let [date, time] = dateTime.split(' ');
    date = date.replaceAll('/', '-');
    let [returnDate, returnTime] = returnDateTime.split(' ');
    returnDate = returnDate.replaceAll('/', '-');
    let outgoingOptions = {
        mode: "json",
        args: [origin, destination, date, time, passengers, returnDate, returnTime]
    };
    let returnOptions = {
        mode: 'json',
        args: [destination, origin, returnDate, returnTime, passengers]
    };
    // RUN SCRIPTS
    let trenitaliaOutgoing = pyrun('toutgoing.py', outgoingOptions);
    let italoOutgoing = pyrun('ioutgoing.py', outgoingOptions);
    let trenitaliaReturn = pyrun('toneway.py', returnOptions);
    let italoReturn = pyrun('ioneway.py', returnOptions);
    Promise.all([trenitaliaOutgoing, italoOutgoing, trenitaliaReturn, italoReturn])
        .then((results) => {
        let resultValue = {
            error: results.map(result => result.error).join(''),
            results: { outgoing: [...results[0].results, ...results[1].results], returning: [...results[2].results, ...results[3].results] },
            metadata: { italo: { cookies: results[1].cookies }, trenitalia: { cookies: results[0].cookies, cartId: results[0].cartId } }
        };
        res.json(resultValue);
    })
        .catch(e => {
        console.log('Encountered an error while looking for one way trips going out and back for both companies');
        console.log(e.message);
    });
});
app.post('/outgoing', (req, res) => {
    const { origin, destination, dateTime, returnDateTime, passengers } = req.body;
    let [date, time] = dateTime.split(' ');
    date = date.replaceAll('/', '-');
    let [returnDate, returnTime] = returnDateTime.split(' ');
    returnDate = returnDate.replaceAll('/', '-');
    // SET OPTIONS
    let options = {
        mode: 'json',
        args: [origin, destination, date, time, passengers, returnDate, returnTime]
    };
    // RUN SCRIPTS
    let trenitaliaResult = pyrun('toutgoing.py', options);
    let italoResult = pyrun('ioutgoing.py', options);
    Promise.all([trenitaliaResult, italoResult])
        .then((results) => {
        let resultValue = {
            error: results[0].error + results[1].error,
            results: [...results[0].results, ...results[1].results],
            metadata: { italoCookies: results[1].cookies, trenitaliaCookies: results[0].cookies, cartId: results[0].cartId }
        };
        res.json(resultValue);
    })
        .catch(e => {
        console.log('Encountered an error while searching for outgoing results');
        console.log(e.message);
    });
});
app.listen(3003, () => {
    console.log('Listening on port 3003');
});
//# sourceMappingURL=index.js.map