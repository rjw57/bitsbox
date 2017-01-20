// Run as e.g.
//
// node fetch_schema.js http://localhost:5000/graphql/ schema

const fetch = require('node-fetch');
const fs = require('fs');
const util = require('graphql/utilities');
const commander = require('commander');

options = {};

commander
  .arguments('<endpoint> [output]')
  .action((endpoint, output) => {
    options.endpoint = endpoint;
    options.output = output || 'schema';
  })
  .parse(process.argv);

// Save JSON of full schema introspection for Babel Relay Plugin to use
fetch(`${options.endpoint}`, {
  method: 'POST',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({'query': util.introspectionQuery}),
}).then(res => res.json()).then(schemaJSON => {
  fs.writeFileSync(
    `${options.output}.json`,
    JSON.stringify(schemaJSON, null, 2)
  );

  // Save user readable type system shorthand of schema
  const graphQLSchema = util.buildClientSchema(schemaJSON.data);
  fs.writeFileSync(
    `${options.output}.graphql`,
    util.printSchema(graphQLSchema)
  );
});
