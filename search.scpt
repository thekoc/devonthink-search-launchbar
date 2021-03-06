JsOsaDAS1.001.00bplist00�Vscript_function getArgv() {
    var args = $.NSProcessInfo.processInfo.arguments;

    // Build the normal argv/argc
    var argv = [];
    var argc = args.count; // -[NSArray count]

    for (var i = 0; i < argc; i++) {
        argv.push(ObjC.unwrap(args.objectAtIndex(i))); // -[NSArray objectAtIndex:]
    }
    delete args;

    return argv;
}

function run() {
    let dtp = Application("DEVONthink Pro");

    let query = getArgv()[4];

    let records = dtp.search(query, {'within': 'titles'});

    results = records.map((r) => {
        return {
            name: r.name(),
            filename: r.filename(),
            path: r.path(),
            location: r.location(),
            referenceURL: r.referenceURL(),
            score: r.score(),
            // thumbnail: r.thumbnail(),
            uuid: r.uuid(),
            type: r.type(),
            kind: r.kind()
        }
    })
    // results.sort(function(a, b) {
    //     return (a.score > b.score) ? -1 : (a.score < b.score) ? 1 : 0;
    // });

    // return JSON.stringify(results);
}
                              5 jscr  ��ޭ