function getDb(dtp, uuid) {
    let db = dtp.getRecordWithUuid(uuid);
    return db;
}

function search(dtp, query, dbUuids) {
    let records = [];
    for (let uuid of dbUuids) {
        records = records.concat(dtp.search(query, {in: dtp.getRecordWithUuid(uuid)}));
    }
    return records;
}

function run(argv) {
    let dtp = Application("DEVONthink 3");

    let jsonArg = JSON.parse(argv[0])
    let field = jsonArg.field;
    let scope = jsonArg.scope;
    let dbUuids = [];
    if (scope) {
        dbUuids = scope;
    } else {
        for (let d of dtp.databases()) {
            dbUuids.push(d.uuid());
        }
    }
    let query = jsonArg.query;
    let range = jsonArg.range;

    let toJson;
    if (field == 'all') {

        toJson = (r) => {
            let uuid = r.uuid();
            return {
                name: r.name(),
                filename: r.filename(),
                path: r.path(),
                location: r.location(),
                referenceURL: 'x-devonthink-item://' + uuid,
                score: r.score(),
                // thumbnail: r.thumbnail(),
                uuid: uuid,
                type: r.type(),
                kind: r.kind()
            }
        }
    } else {
        toJson = (r) => {
            return {
                score: r.score(),
                uuid: r.uuid(),
                modificationDate: r.modificationDate()
            }
        }
    }

    // let records = dtp.search(query, {'within': 'titles'});
    let records = search(dtp, query, dbUuids);
    if (range) {
        let [begin, end] = range;
        records = records.slice(begin, end);
    }

    results = records.map(toJson)
    // results.sort(function(a, b) {
    //     return (a.score > b.score) ? -1 : (a.score < b.score) ? 1 : 0;
    // });

    return JSON.stringify(results);
}
