function run(uuid) {
    let dtp = Application("DEVONthink 3");

    let groupUuid = uuid.toString()
    let group = dtp.getRecordWithUuid(groupUuid)

    let records = group.children()

    results = records.map((r) => {
        return {
            name: r.name(),
            filename: r.filename(),
            path: r.path(),
            location: r.location(),
            // referenceURL: r.referenceURL(),
            score: r.score(),
            // thumbnail: r.thumbnail(),
            uuid: r.uuid(),
            type: r.type(),
            kind: r.kind()
        }
    })

    return JSON.stringify(results);
}
