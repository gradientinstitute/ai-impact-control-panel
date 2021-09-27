import React, {useState, useEffect, useReducer, useContext} from 'react';

export function IntroPane(props) {

  const metadata = {

    name: "EzyFraud Pro",
    purpose: "to detect and prevent credit card fraud.",
    operation: "the system analyses credit card transactions coming into the bank, blocking those which it predicts to be fraudulent.  An SMS is then sent to the customer, giving them an opportiunity to confirm the legitimacy of the transaction.",
    actions: {
      allow : "allows the transaction to proceed",
      block : "prevents the transaction from occuring, and sends an sms to the customer asking them to confirm the legitimacy of the transaction. If they confirm, then the system will whitelist the transaction so they can re-attempt it."
    },
    targets: {
      fraudulent: "The transaction is fraudulent, i.e. not being conducted with the informed consent of the customer",
    },
    data: "The system is trained with historical transaction data collected by the bank in the last financial year. Positive labels are assumed for undisputed transactions, negative labels come from fraud investigations",
    candidates: "Candidate models have been generated by hyperparameter sweeps.",
    objectives: {
      catch_fraud: {
        description: "Prevent as many fraudulent transactions as possible for the sake of the bank and the customers",
      },
      avoid_interference: {
        description: "Minimise the number of legitimate transactions blocked to prevent annoying customers",
      },
      minimise_excessive_interfence: {
        description: "Prevent any customers from experiencing exessive false blockings",
      },
      dont_disadvantage_women: {
        description: "Ensure system doesnt make more errors on women",
      }
    },
    metrics: props.units,
  }


  function rows() {
    let result = [];
    for (const [name, d] of Object.entries(props.units)) {
      const deets = JSON.stringify(d, null, 2);
      result.push(
        <div key={name}>
          <h2>{name}</h2>
          <pre className="text-left">{deets}</pre>
        </div>
      );
    }
    return result;
  }

  function actions() {
    let result = [];
    for (const [name, d] of Object.entries(metadata.actions)) {
      result.push(
        <div key={name} className="">
          <h2>{name}</h2>
          <p>{d}</p>
        </div>
      );
    }
    return result;
  }

  function objectives() {
    let result = [];
    for (const [name, d] of Object.entries(metadata.objectives)) {
      result.push (
        <div key={name} className="bg-yellow-100">
          <p>{d.description}</p>
        </div>
      );
    }
    return result;
  }

  return (
    <div className="mx-auto text-base max-w-prose">
      <h1> {metadata.name} </h1>
      <p>A system {metadata.purpose}</p>
      <p>{metadata.operation}</p>

      <h2> Objectives </h2>
      <div className="flex space-x-10">
        {objectives()}
      </div>

      <h2> System Actions</h2>
      <div className="flex space-x-10">
        {actions()}
      </div>

      <h2> Data </h2>
      <p>{metadata.data}</p>

      <div className="flex flex-wrap space-x-10 mt-8">
        {rows()}
      </div>
      <ReadyButton onClick={props.onClick} />
    </div>
  );
}

function ReadyButton(props) {
  return (
      <button className="bg-yellow-300 rounded-lg" 
        onClick={() => props.onClick()}>
        <div className="p-4">
          Begin
        </div>
      </button>
  );
}

