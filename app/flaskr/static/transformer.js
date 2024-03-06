import { pipeline } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers';

// Transformer class to encode definitions to vector representations
export default class Transformer {
    constructor(model = "multi-qa-distilbert-cos-v1") {
        this.model = model;
    }

    // Download the model passed in the constructor
    async create_extractor() {
        this.extractor = await pipeline('feature-extraction', 'Xenova/' + this.model);
    }

    // Return a matrix containing vector representations of the sentences.
    // Sentences: either a list of strings, or a string.
    async encode(sentences) {
        var output = await this.extractor(sentences, { pooling: 'mean', normalize: true });
        return output;
    }
}
