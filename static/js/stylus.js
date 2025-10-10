/**
 * Stylus Drawing Script for MathScriber
 * Supports stylus, pen, touch, and mouse input using Pointer Events API
 */

class StylusDrawing {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.isDrawing = false;
        this.strokes = []; // Store strokes for undo functionality
        this.currentStroke = [];
        this.lastPoint = null;
        this.eraseRedrawPending = false; // Flag to prevent too frequent eraser redraws
        
        // Drawing settings
        this.brushSize = 3;
        this.brushColor = '#000000';
        this.isEraserMode = false;
        this.eraserSize = 10;
        
        // Canvas dimensions
        this.canvasWidth = 0;
        this.canvasHeight = 0;
        this.scale = 1;
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        this.canvas = document.getElementById('drawing-canvas');
        this.ctx = this.canvas.getContext('2d');
        
        if (!this.canvas || !this.ctx) {
            console.error('Canvas not found');
            return;
        }
        
        this.setupCanvas();
        this.setupEventListeners();
        this.setupControls();
        this.updateStatus('Ready to draw');
    }
    
    setupCanvas() {
        // Set canvas size to fill container
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // Set actual size (scale for high DPI displays)
        this.scale = window.devicePixelRatio || 1;
        this.canvasWidth = rect.width;
        this.canvasHeight = rect.height;
        
        this.canvas.width = this.canvasWidth * this.scale;
        this.canvas.height = this.canvasHeight * this.scale;
        
        // Set display size
        this.canvas.style.width = this.canvasWidth + 'px';
        this.canvas.style.height = this.canvasHeight + 'px';
        
        // Scale context for high DPI
        this.ctx.scale(this.scale, this.scale);
        
        // Set default drawing properties
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.imageSmoothingEnabled = true;
        
        this.updateCanvasInfo();
        
        // Handle resize
        window.addEventListener('resize', () => {
            setTimeout(() => this.handleResize(), 100);
        });
    }
    
    setupEventListeners() {
        // Pointer Events (supports stylus, pen, touch, mouse)
        this.canvas.addEventListener('pointerdown', (e) => this.handlePointerDown(e));
        this.canvas.addEventListener('pointermove', (e) => this.handlePointerMove(e));
        this.canvas.addEventListener('pointerup', (e) => this.handlePointerUp(e));
        this.canvas.addEventListener('pointercancel', (e) => this.handlePointerUp(e));
        
        // Prevent context menu on long press
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // Prevent scrolling/zooming while drawing
        this.canvas.addEventListener('touchstart', (e) => e.preventDefault());
        this.canvas.addEventListener('touchmove', (e) => e.preventDefault());
    }
    
    setupControls() {
        // Color picker
        const colorPicker = document.getElementById('pen-color');
        if (colorPicker) {
            colorPicker.addEventListener('change', (e) => {
                this.brushColor = e.target.value;
            });
        }
        
        // Brush size
        const brushSize = document.getElementById('brush-size');
        const sizeDisplay = document.getElementById('size-display');
        if (brushSize && sizeDisplay) {
            brushSize.addEventListener('input', (e) => {
                this.brushSize = parseInt(e.target.value);
                sizeDisplay.textContent = this.brushSize + 'px';
            });
        }
        
        // Eraser size
        const eraserSize = document.getElementById('eraser-size');
        const eraserSizeDisplay = document.getElementById('eraser-size-display');
        if (eraserSize && eraserSizeDisplay) {
            eraserSize.addEventListener('input', (e) => {
                this.eraserSize = parseInt(e.target.value);
                eraserSizeDisplay.textContent = this.eraserSize + 'px';
            });
        }
        
        // Pen/Eraser mode buttons
        const penModeBtn = document.getElementById('pen-mode-btn');
        const eraserModeBtn = document.getElementById('eraser-mode-btn');
        const eraserSizeGroup = document.getElementById('eraser-size-group');
        
        if (penModeBtn) {
            penModeBtn.addEventListener('click', () => {
                this.isEraserMode = false;
                penModeBtn.classList.add('active');
                eraserModeBtn.classList.remove('active');
                if (eraserSizeGroup) eraserSizeGroup.style.display = 'none';
                this.canvas.style.cursor = 'crosshair';
                this.canvas.classList.remove('eraser-mode');
                this.updateStatus('Pen mode activated');
            });
        }
        
        if (eraserModeBtn) {
            eraserModeBtn.addEventListener('click', () => {
                this.isEraserMode = true;
                eraserModeBtn.classList.add('active');
                penModeBtn.classList.remove('active');
                if (eraserSizeGroup) eraserSizeGroup.style.display = 'inline';
                this.canvas.style.cursor = 'grab';
                this.canvas.classList.add('eraser-mode');
                this.updateStatus('Eraser mode activated');
            });
        }
        
        // Clear button
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearCanvas());
        }
        
        // Undo button
        const undoBtn = document.getElementById('undo-btn');
        if (undoBtn) {
            undoBtn.addEventListener('click', () => this.undo());
        }
        
        // Save PDF button
        const savePdfBtn = document.getElementById('save-pdf-btn');
        if (savePdfBtn) {
            savePdfBtn.addEventListener('click', () => this.savePDF());
        }
        
        // Upload button
        const uploadBtn = document.getElementById('upload-btn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.uploadToConverter());
        }
    }
    
    getPointerPosition(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
            pressure: e.pressure || 0.5
        };
    }
    
    handlePointerDown(e) {
        e.preventDefault();
        this.isDrawing = true;
        this.currentStroke = [];
        
        const pos = this.getPointerPosition(e);
        this.lastPoint = pos;
        
        if (this.isEraserMode) {
            // Eraser mode - find and remove strokes that intersect with eraser position
            this.eraseAtPosition(pos.x, pos.y);
        } else {
            // Drawing mode
            this.currentStroke.push(pos);
            
            // Set drawing style
            this.ctx.strokeStyle = this.brushColor;
            this.ctx.lineWidth = this.brushSize * (e.pressure || 0.5);
            
            // Start new path
            this.ctx.beginPath();
            this.ctx.moveTo(pos.x, pos.y);
        }
        
        this.updateStatus(`${this.isEraserMode ? 'Erasing' : 'Drawing'} with ${e.pointerType} (pressure: ${(e.pressure || 0.5).toFixed(2)})`);
    }
    
    handlePointerMove(e) {
        if (!this.isDrawing) return;
        
        e.preventDefault();
        const pos = this.getPointerPosition(e);
        
        if (this.isEraserMode) {
            // Continue erasing
            this.eraseAtPosition(pos.x, pos.y);
        } else {
            // Continue drawing
            this.currentStroke.push(pos);
            
            // Vary line width based on pressure (if available)
            if (e.pressure) {
                this.ctx.lineWidth = this.brushSize * e.pressure;
            }
            
            // Draw smooth line
            if (this.lastPoint) {
                this.ctx.quadraticCurveTo(
                    this.lastPoint.x, this.lastPoint.y,
                    pos.x, pos.y
                );
                this.ctx.stroke();
            }
        }
        
        this.lastPoint = pos;
    }
    
    handlePointerUp(e) {
        if (!this.isDrawing) return;
        
        e.preventDefault();
        this.isDrawing = false;
        
        // Finish the current stroke (only save if not in eraser mode and has points)
        if (!this.isEraserMode && this.currentStroke.length > 0) {
            this.strokes.push({
                points: [...this.currentStroke],
                color: this.brushColor,
                size: this.brushSize,
                timestamp: Date.now() // Add timestamp for debugging
            });
            console.log(`Stroke saved: ${this.currentStroke.length} points, total strokes: ${this.strokes.length}`);
        }
        
        this.currentStroke = [];
        this.lastPoint = null;
        this.updateStatus('Ready to draw');
    }
    
    eraseAtPosition(x, y) {
        let erasedSomething = false;
        const eraserRadius = this.eraserSize / 2;
        
        // Remove strokes that intersect with the eraser area
        this.strokes = this.strokes.filter(stroke => {
            // Check if any point in the stroke is within eraser radius
            const shouldKeep = !stroke.points.some(point => {
                const distance = Math.sqrt(
                    Math.pow(point.x - x, 2) + Math.pow(point.y - y, 2)
                );
                return distance <= eraserRadius;
            });
            
            if (!shouldKeep) {
                erasedSomething = true;
            }
            
            return shouldKeep;
        });
        
        // Only redraw if something was actually erased to improve performance
        if (erasedSomething) {
            // Use requestAnimationFrame to avoid too frequent redraws
            if (!this.eraseRedrawPending) {
                this.eraseRedrawPending = true;
                requestAnimationFrame(() => {
                    this.redrawCanvas();
                    this.eraseRedrawPending = false;
                });
            }
        }
    }
    
    clearCanvas() {
        if (this.strokes.length === 0) {
            this.updateStatus('Canvas is already empty');
            return;
        }
        
        if (confirm('Are you sure you want to clear the entire canvas?')) {
            // Clear all strokes
            this.strokes = [];
            this.currentStroke = [];
            
            // Clear the canvas while preserving the current transform
            this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
            
            this.updateStatus('Canvas cleared');
        }
    }
    
    undo() {
        if (this.strokes.length === 0) {
            this.updateStatus('Nothing to undo');
            return;
        }
        
        // Remove last stroke
        const removedStroke = this.strokes.pop();
        
        // Redraw all remaining strokes efficiently
        requestAnimationFrame(() => {
            this.redrawCanvas();
        });
        
        this.updateStatus(`Last stroke undone (${this.strokes.length} strokes remaining)`);
    }
    
    redrawCanvas() {
        // Clear the entire canvas while preserving the current transform
        this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
        
        // Redraw all strokes
        this.strokes.forEach(stroke => {
            if (stroke.points.length === 0) return;
            
            this.ctx.strokeStyle = stroke.color;
            this.ctx.lineWidth = stroke.size;
            this.ctx.beginPath();
            
            // Draw the stroke
            this.ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
            for (let i = 1; i < stroke.points.length; i++) {
                const point = stroke.points[i];
                const prevPoint = stroke.points[i - 1];
                
                this.ctx.quadraticCurveTo(
                    prevPoint.x,
                    prevPoint.y,
                    (point.x + prevPoint.x) / 2,
                    (point.y + prevPoint.y) / 2
                );
            }
            this.ctx.stroke();
        });
    }
    
    async savePDF() {
        try {
            this.updateStatus('Generating PDF...');
            
            // Get canvas as image
            const imageData = this.canvas.toDataURL('image/png');
            
            // Create PDF using jsPDF
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF({
                orientation: 'landscape',
                unit: 'px',
                format: [this.canvas.width / (window.devicePixelRatio || 1), 
                        this.canvas.height / (window.devicePixelRatio || 1)]
            });
            
            // Add image to PDF
            pdf.addImage(imageData, 'PNG', 0, 0, 
                        this.canvas.width / (window.devicePixelRatio || 1), 
                        this.canvas.height / (window.devicePixelRatio || 1));
            
            // Download PDF
            const fileName = `stylus-drawing-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.pdf`;
            pdf.save(fileName);
            
            this.updateStatus('PDF saved successfully');
        } catch (error) {
            console.error('Error saving PDF:', error);
            this.updateStatus('Error saving PDF');
            alert('Error saving PDF. Please try again.');
        }
    }
    
    async uploadToConverter() {
        if (this.strokes.length === 0) {
            alert('Please draw something before uploading');
            return;
        }
        
        try {
            this.updateStatus('Preparing upload...');
            
            // Convert canvas to blob
            const blob = await new Promise(resolve => {
                this.canvas.toBlob(resolve, 'image/png', 1.0);
            });
            
            // Create file from blob
            const fileName = `stylus-drawing-${Date.now()}.png`;
            const file = new File([blob], fileName, { type: 'image/png' });
            
            // Create form data
            const formData = new FormData();
            formData.append('images', file);
            formData.append('task', 'equation');
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Upload to converter
            this.updateStatus('Uploading to converter...');
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            
            if (response.ok) {
                this.updateStatus('Upload successful! Redirecting...');
                // Redirect to results page
                window.location.href = '/upload/';
            } else {
                throw new Error('Upload failed');
            }
            
        } catch (error) {
            console.error('Error uploading:', error);
            this.updateStatus('Upload failed');
            alert('Error uploading to converter. Please try again.');
        }
    }
    
    handleResize() {
        // Save current strokes data instead of image data to avoid scaling issues
        const savedStrokes = JSON.parse(JSON.stringify(this.strokes));
        
        // Resize canvas
        this.setupCanvas();
        
        // Restore strokes
        this.strokes = savedStrokes;
        this.redrawCanvas();
        this.updateCanvasInfo();
    }
    
    updateCanvasInfo() {
        const info = document.getElementById('canvas-dimensions');
        if (info) {
            const displayWidth = this.canvas.style.width;
            const displayHeight = this.canvas.style.height;
            info.textContent = `${displayWidth} × ${displayHeight}`;
        }
    }
    
    updateStatus(message) {
        const statusText = document.getElementById('status-text');
        if (statusText) {
            statusText.textContent = message;
        }
        console.log('Stylus:', message);
    }
}

// Initialize the drawing app
new StylusDrawing();