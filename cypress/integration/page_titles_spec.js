import supplyChains from '../fixtures/supplyChains.json';
import strategicActions from '../fixtures/strategicActions.json';
import strategicActionUpdates from '../fixtures/strategicActionUpdates.json';

const supplyChain = supplyChains.find((supplyChain) => supplyChain.fields.slug === 'supply-chain-7');
const strategicAction = strategicActions.find((strategicAction) => strategicAction.fields.supply_chain === supplyChain.pk && strategicAction.fields.slug === 'sa-title-test')
const strategicActionUpdate = strategicActionUpdates.find((strategicActionUpdate) => strategicActionUpdate.fields.strategic_action === strategicAction.pk && strategicActionUpdate.fields.slug === '05-2021');

import { urlBuilder } from "../support/utils.js"

const urls = urlBuilder(supplyChain, strategicAction, strategicActionUpdate);

const expectedTitles = {
    home: () => 'Update supply chain information',
    supplyChain: {
        taskList: () => `Update ${supplyChain.fields.name} – ${expectedTitles.home()}`,
        summary: () => `Summary – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
        strategicActions: {
            summary: () => `Strategic actions – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
            update: {
                info: () => `Update information - ${strategicAction.fields.name} update – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
                timing: () => `Expected completion date - ${strategicAction.fields.name} update – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
                status: () => `Current delivery status - ${strategicAction.fields.name} update – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
                revisedTiming: () => `Revised expected completion date - ${strategicAction.fields.name} update – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
                confirm: () => `Check your answers - ${strategicAction.fields.name} update – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
                review: () => `Current monthly update - ${strategicAction.fields.name} – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
            }
        },
        updateComplete: () => `Update complete – ${supplyChain.fields.name} – ${expectedTitles.home()}`,
    }
};


describe('The Home Page', () => {
    it('has the correct title', () => {
        cy.visit(urls.home);
        cy.title().should('equal', expectedTitles.home());
    });
});

describe('The Task List page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.taskList);
        cy.title().should('equal', expectedTitles.supplyChain.taskList())
    });
});

describe('The Supply Chain Summary page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.summary);
        cy.title().should('equal', expectedTitles.supplyChain.summary())
    });
});

describe('The Strategic Actions Summary page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.strategicActions.summary);
        cy.title().should('equal', expectedTitles.supplyChain.strategicActions.summary())
    });
});

describe('The Strategic Action Update Info page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.strategicActions.update.info);
        cy.title().should('equal', expectedTitles.supplyChain.strategicActions.update.info())
    });
});

describe('The Strategic Action Update Timing page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.strategicActions.update.timing);
        cy.title().should('equal', expectedTitles.supplyChain.strategicActions.update.timing())
    });
});

describe('The Strategic Action Update Status page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.strategicActions.update.status);
        cy.title().should('equal', expectedTitles.supplyChain.strategicActions.update.status())
    });
});

describe('The Strategic Action Update Revised Timing page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.strategicActions.update.revisedTiming);
        cy.title().should('equal', expectedTitles.supplyChain.strategicActions.update.revisedTiming())
    });
});

describe('The Strategic Action Update Check Your Answers page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.strategicActions.update.confirm);
        cy.title().should('equal', expectedTitles.supplyChain.strategicActions.update.confirm())
    });
});

describe('The Strategic Action Update Complete page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.taskList);
        cy.mainForm().submitButton().click()
        cy.title().should('equal', expectedTitles.supplyChain.updateComplete())
    });
});

describe('The Strategic Action Update Review page', () => {
    it('has the correct title', () => {
        cy.visit(urls.supplyChain.taskList);
        cy.get(`#updates .govuk-link[href="${urls.supplyChain.strategicActions.update.review}"]`).click()
        cy.title().should('equal', expectedTitles.supplyChain.strategicActions.update.review())
    });
});
