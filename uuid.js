function run(argv) {
    let dtp = Application("DEVONthink 3");
    let records = []
    for (let uuid of argv) {
        let r = dtp.getRecordWithUuid(uuid)
        records.push({
            name: r.name(),
            filename: r.filename(),
            path: r.path(),
            location: r.location(),
            referenceURL: r.referenceURL(),
            // score: r.score(),
            // thumbnail: r.thumbnail(),
            uuid: r.uuid(),
            type: r.type(),
            kind: r.kind() 
        })
    }
    // return  uuid
    return JSON.stringify(records)
}