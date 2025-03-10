from flask import Flask, render_template, request, jsonify
import random
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

class Microorganism:
    def __init__(self, name, organism_type, health):
        self.name = name
        self.type = organism_type
        self.health = health
        self.position = (random.uniform(0, 10), random.uniform(0, 10))  # Random position in a 10x10 area

    def interact(self, other):
        # Interaction logic (same as your current logic)
        if self.type == 'good_bacteria' and other.type == 'bad_bacteria':
            damage = 0.1 * other.health * random.uniform(0.5, 1.5)
            other.health -= damage
        elif self.type == 'bad_bacteria' and other.type == 'good_bacteria':
            damage = 0.1 * other.health * random.uniform(0.5, 1.5)
            other.health -= damage
        elif self.type == 'good_bacteria' and other.type == 'virus':
            damage = 0.1 * other.health * random.uniform(0.5, 1.5)
            self.health -= damage
        elif self.type == 'fungi' and other.type == 'good_bacteria':
            recovery = 0.05 * other.health * random.uniform(0.5, 1.5)
            self.health += recovery
        elif self.type == 'fungi' and other.type == 'bad_bacteria':
            damage = 0.05 * other.health * random.uniform(0.5, 1.5)
            self.health -= damage

        self.health = max(self.health, 0)

    def is_healthy(self):
        if self.type == "good_bacteria":
            return self.health > 0.1
        return self.health > 0.3

class MicrobiomeSimulation:
    def __init__(self, num_bacteria, num_viruses, num_fungi, num_iterations, digestion_rate, healthy_bacteria_ratio):
        self.num_bacteria = num_bacteria
        self.num_viruses = num_viruses
        self.num_fungi = num_fungi
        self.num_iterations = num_iterations
        self.digestion_rate = digestion_rate
        self.healthy_bacteria_ratio = healthy_bacteria_ratio
        self.microorganisms_list = self.initialize_microorganisms()

    def initialize_microorganisms(self):
        microorganisms = []
        num_good_bacteria = int(self.num_bacteria * self.healthy_bacteria_ratio)
        num_bad_bacteria = self.num_bacteria - num_good_bacteria

        for index in range(num_good_bacteria):
            microorganisms.append(Microorganism(f'GoodBacteria_{index}', 'good_bacteria', random.uniform(0.5, 1.0)))
        for index in range(num_bad_bacteria):
            microorganisms.append(Microorganism(f'BadBacteria_{index}', 'bad_bacteria', random.uniform(0.1, 0.5)))
        for index in range(self.num_viruses):
            microorganisms.append(Microorganism(f'Virus_{index}', 'virus', random.uniform(0.1, 0.5)))
        for index in range(self.num_fungi):
            microorganisms.append(Microorganism(f'Fungi_{index}', 'fungi', random.uniform(0.5, 1.0)))

        return microorganisms

    def simulate(self):
        healthy_bacteria_counts = []
        for iteration in range(self.num_iterations):
            for i in range(len(self.microorganisms_list)):
                for j in range(len(self.microorganisms_list)):
                    if i != j:
                        self.microorganisms_list[i].interact(self.microorganisms_list[j])
            healthy_count = sum(1 for m in self.microorganisms_list if m.type == 'good_bacteria' and m.is_healthy())
            healthy_bacteria_counts.append(healthy_count)
            for m in self.microorganisms_list:
                if m.type == 'good_bacteria':
                    m.health -= self.digestion_rate * (1 - self.healthy_bacteria_ratio)
                    if m.is_healthy() and random.random() < 0.5:
                        m.health += 0.05
                    m.health = min(m.health, 1.0)
        return healthy_bacteria_counts

    def generate_plot(self, healthy_bacteria_count_list):
        plt.plot(healthy_bacteria_count_list)
        plt.title('Healthy Good Bacteria Count Over Time')
        plt.xlabel('Iteration')
        plt.ylabel('Healthy Good Bacteria Count')
        plt.grid()

        # Save plot to a BytesIO object and encode as base64
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        return plot_url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    num_bacteria = int(request.form['num_bacteria'])
    num_viruses = int(request.form['num_viruses'])
    num_fungi = int(request.form['num_fungi'])
    num_iterations = int(request.form['num_iterations'])
    healthy_bacteria_ratio = float(request.form['healthy_bacteria_ratio'])
    digestion_rate = 0.1

    simulation = MicrobiomeSimulation(num_bacteria, num_viruses, num_fungi, num_iterations, digestion_rate, healthy_bacteria_ratio)
    healthy_bacteria_count_list = simulation.simulate()
    plot_url = simulation.generate_plot(healthy_bacteria_count_list)

    return jsonify({'plot_url': plot_url})

if __name__ == '__main__':
    app.run(debug=True)
