#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pdf2image", "pillow"]
# ///


#!/usr/bin/env python3
"""
PDF Slide Viewer Generator

Converts PDF presentations to images and creates a responsive HTML viewer
for quickly browsing through all slides.

Requirements:
    pip install pdf2image pillow

Usage:
    python pdf_viewer.py /path/to/pdfs/
    python pdf_viewer.py file1.pdf file2.pdf file3.pdf
    python pdf_viewer.py --single-file presentation.pdf  # Creates self-contained HTML
"""

import os
import sys
import argparse
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import json
import base64
from io import BytesIO

class PDFSlideViewer:
    def __init__(self, output_dir="slide_viewer", thumbnail_size=(300, 200), quality=85, single_file=False):
        self.output_dir = Path(output_dir)
        self.thumbnail_size = thumbnail_size
        self.quality = quality
        self.single_file = single_file
        self.slides_data = []

    def setup_directories(self):
        """Create necessary directories"""
        self.output_dir.mkdir(exist_ok=True)
        if not self.single_file:
            (self.output_dir / "images").mkdir(exist_ok=True)
            (self.output_dir / "thumbnails").mkdir(exist_ok=True)

    def image_to_base64(self, image, format="PNG"):
        """Convert PIL Image to base64 data URI"""
        buffer = BytesIO()
        image.save(buffer, format=format, quality=self.quality, optimize=True)
        img_data = buffer.getvalue()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        return f"data:image/{format.lower()};base64,{img_base64}"

    def convert_pdf_to_images(self, pdf_path):
        """Convert a single PDF to images"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists() or pdf_path.suffix.lower() != '.pdf':
            print(f"Skipping {pdf_path}: not a valid PDF file")
            return []

        print(f"Processing {pdf_path.name}...")

        try:
            # Convert PDF to images
            pages = convert_from_path(pdf_path, dpi=150)
            slide_info = []

            presentation_name = pdf_path.stem

            for i, page in enumerate(pages):
                if self.single_file:
                    # Create thumbnail
                    thumbnail = page.copy()
                    thumbnail.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)

                    # Convert to base64
                    img_data_uri = self.image_to_base64(page)
                    thumb_data_uri = self.image_to_base64(thumbnail)

                    slide_info.append({
                        'presentation': presentation_name,
                        'page': i + 1,
                        'image': img_data_uri,
                        'thumbnail': thumb_data_uri,
                        'id': f"{presentation_name}_page_{i+1}"
                    })
                else:
                    # Save to files (original behavior)
                    img_filename = f"{presentation_name}_page_{i+1:03d}.png"
                    thumb_filename = f"{presentation_name}_page_{i+1:03d}_thumb.png"

                    img_path = self.output_dir / "images" / img_filename
                    thumb_path = self.output_dir / "thumbnails" / thumb_filename

                    # Save full image
                    page.save(img_path, "PNG", quality=self.quality, optimize=True)

                    # Create and save thumbnail
                    page.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                    page.save(thumb_path, "PNG", quality=self.quality, optimize=True)

                    slide_info.append({
                        'presentation': presentation_name,
                        'page': i + 1,
                        'image': f"images/{img_filename}",
                        'thumbnail': f"thumbnails/{thumb_filename}",
                        'id': f"{presentation_name}_page_{i+1}"
                    })

            print(f"  Converted {len(pages)} slides from {pdf_path.name}")
            return slide_info

        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return []

    def process_pdfs(self, pdf_paths):
        """Process multiple PDF files"""
        self.setup_directories()

        for pdf_path in pdf_paths:
            slides = self.convert_pdf_to_images(pdf_path)
            self.slides_data.extend(slides)

    def generate_html_viewer(self):
        """Generate the HTML viewer"""

        # Group slides by presentation
        presentations = {}
        for slide in self.slides_data:
            pres_name = slide['presentation']
            if pres_name not in presentations:
                presentations[pres_name] = []
            presentations[pres_name].append(slide)

        # Calculate approximate file size for single file mode
        file_size_info = ""
        if self.single_file:
            total_chars = sum(len(slide['image']) + len(slide['thumbnail']) for slide in self.slides_data)
            estimated_mb = (total_chars * 0.75) / (1024 * 1024)  # Base64 is ~4/3 larger than binary
            file_size_info = f" (Estimated size: ~{estimated_mb:.1f}MB)"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Slide Viewer{file_size_info}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }}

        .header {{
            background: white;
            padding: 1rem 2rem;
            border-bottom: 1px solid #ddd;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}

        .controls {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}

        .search-box {{
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
            width: 300px;
            max-width: 100%;
        }}

        .view-toggle {{
            display: flex;
            gap: 0.5rem;
        }}

        .view-btn {{
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 4px;
            font-size: 0.9rem;
        }}

        .view-btn.active {{
            background: #007acc;
            color: white;
            border-color: #007acc;
        }}

        .stats {{
            font-size: 0.9rem;
            color: #666;
        }}

        .container {{
            padding: 2rem;
        }}

        .presentation-section {{
            margin-bottom: 3rem;
        }}

        .presentation-title {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            padding: 0.5rem 0;
            border-bottom: 2px solid #007acc;
            color: #007acc;
        }}

        .slides-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
        }}

        .slides-list {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .slide-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}

        .slide-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}

        .slide-image {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .slide-info {{
            padding: 0.75rem;
            font-size: 0.9rem;
            color: #666;
            border-top: 1px solid #eee;
        }}

        /* List view specific */
        .list-view .slide-card {{
            display: flex;
            align-items: center;
            padding: 1rem;
        }}

        .list-view .slide-image {{
            width: 120px;
            height: auto;
            margin-right: 1rem;
            border-radius: 4px;
        }}

        .list-view .slide-info {{
            padding: 0;
            border: none;
            flex: 1;
        }}

        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 1000;
            overflow: auto;
        }}

        .modal-content {{
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 2rem;
            position: relative;
        }}

        .modal-image {{
            max-width: 90%;
            max-height: 90vh;
            object-fit: contain;
        }}

        .modal-nav {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 1rem;
            font-size: 2rem;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.2s;
        }}

        .modal-nav:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}

        .modal-prev {{
            left: 2rem;
        }}

        .modal-next {{
            right: 2rem;
        }}

        .modal-close {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            color: white;
            border: none;
            font-size: 2rem;
            cursor: pointer;
            padding: 0.5rem;
        }}

        .modal-info {{
            position: absolute;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .header {{
                padding: 1rem;
            }}

            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}

            .search-box {{
                width: 100%;
            }}

            .container {{
                padding: 1rem;
            }}

            .slides-grid {{
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            }}

            .modal-nav {{
                padding: 0.5rem;
                font-size: 1.5rem;
            }}

            .modal-prev {{
                left: 1rem;
            }}

            .modal-next {{
                right: 1rem;
            }}
        }}

        .hidden {{
            display: none !important;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PDF Slide Viewer{"" if not self.single_file else " (Single File)"}</h1>
        <div class="controls">
            <input type="text" class="search-box" placeholder="Search presentations or slides..." id="searchBox">
            <div class="view-toggle">
                <button class="view-btn active" data-view="grid">Grid</button>
                <button class="view-btn" data-view="list">List</button>
            </div>
            <div class="stats">
                <span id="slideCount">{len(self.slides_data)}</span> slides from
                <span id="presentationCount">{len(presentations)}</span> presentations
            </div>
        </div>
    </div>

    <div class="container">
        <div id="presentationsContainer">
"""

        # Generate presentation sections
        for pres_name, slides in presentations.items():
            html_content += f"""
            <div class="presentation-section" data-presentation="{pres_name}">
                <div class="presentation-title">{pres_name} ({len(slides)} slides)</div>
                <div class="slides-grid" id="slides-{pres_name.replace(' ', '_')}">
"""

            for slide in slides:
                html_content += f"""
                    <div class="slide-card" data-slide-id="{slide['id']}" data-presentation="{slide['presentation']}" data-page="{slide['page']}">
                        <img src="{slide['thumbnail']}" alt="Slide {slide['page']}" class="slide-image" loading="lazy">
                        <div class="slide-info">
                            Page {slide['page']}
                        </div>
                    </div>
"""

            html_content += """
                </div>
            </div>
"""

        html_content += f"""
        </div>
    </div>

    <!-- Modal -->
    <div class="modal" id="slideModal">
        <div class="modal-content">
            <button class="modal-close" id="modalClose">&times;</button>
            <button class="modal-nav modal-prev" id="modalPrev">&#8249;</button>
            <img src="" alt="" class="modal-image" id="modalImage">
            <button class="modal-nav modal-next" id="modalNext">&#8250;</button>
            <div class="modal-info" id="modalInfo"></div>
        </div>
    </div>

    <script>
        // Slide data
        const slidesData = {json.dumps(self.slides_data, indent=2)};
        let currentSlideIndex = 0;
        let filteredSlides = [...slidesData];

        // Elements
        const searchBox = document.getElementById('searchBox');
        const presentationsContainer = document.getElementById('presentationsContainer');
        const slideModal = document.getElementById('slideModal');
        const modalImage = document.getElementById('modalImage');
        const modalInfo = document.getElementById('modalInfo');
        const modalClose = document.getElementById('modalClose');
        const modalPrev = document.getElementById('modalPrev');
        const modalNext = document.getElementById('modalNext');
        const viewButtons = document.querySelectorAll('.view-btn');

        // Search functionality
        searchBox.addEventListener('input', function() {{
            const query = this.value.toLowerCase();
            const presentations = document.querySelectorAll('.presentation-section');

            presentations.forEach(section => {{
                const presentationName = section.dataset.presentation.toLowerCase();
                const slides = section.querySelectorAll('.slide-card');
                let hasVisibleSlides = false;

                slides.forEach(slide => {{
                    const slideText = `${{slide.dataset.presentation}} page ${{slide.dataset.page}}`.toLowerCase();
                    const isVisible = slideText.includes(query) || presentationName.includes(query);
                    slide.style.display = isVisible ? '' : 'none';
                    if (isVisible) hasVisibleSlides = true;
                }});

                section.style.display = hasVisibleSlides ? '' : 'none';
            }});
        }});

        // View toggle
        viewButtons.forEach(btn => {{
            btn.addEventListener('click', function() {{
                viewButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const view = this.dataset.view;
                const grids = document.querySelectorAll('.slides-grid');

                grids.forEach(grid => {{
                    grid.className = view === 'list' ? 'slides-list' : 'slides-grid';
                }});

                document.body.className = view === 'list' ? 'list-view' : '';
            }});
        }});

        // Modal functionality
        function openModal(slideId) {{
            const slideIndex = slidesData.findIndex(s => s.id === slideId);
            if (slideIndex === -1) return;

            currentSlideIndex = slideIndex;
            showSlide(slideIndex);
            slideModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }}

        function closeModal() {{
            slideModal.style.display = 'none';
            document.body.style.overflow = '';
        }}

        function showSlide(index) {{
            const slide = slidesData[index];
            modalImage.src = slide.image;
            modalImage.alt = `${{slide.presentation}} - Page ${{slide.page}}`;
            modalInfo.textContent = `${{slide.presentation}} - Page ${{slide.page}} of ${{slidesData.filter(s => s.presentation === slide.presentation).length}}`;
        }}

        function nextSlide() {{
            currentSlideIndex = (currentSlideIndex + 1) % slidesData.length;
            showSlide(currentSlideIndex);
        }}

        function prevSlide() {{
            currentSlideIndex = (currentSlideIndex - 1 + slidesData.length) % slidesData.length;
            showSlide(currentSlideIndex);
        }}

        // Event listeners
        document.addEventListener('click', function(e) {{
            if (e.target.closest('.slide-card')) {{
                const slideCard = e.target.closest('.slide-card');
                openModal(slideCard.dataset.slideId);
            }}
        }});

        modalClose.addEventListener('click', closeModal);
        modalPrev.addEventListener('click', prevSlide);
        modalNext.addEventListener('click', nextSlide);

        slideModal.addEventListener('click', function(e) {{
            if (e.target === slideModal) {{
                closeModal();
            }}
        }});

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (slideModal.style.display === 'block') {{
                switch(e.key) {{
                    case 'Escape':
                        closeModal();
                        break;
                    case 'ArrowLeft':
                        prevSlide();
                        break;
                    case 'ArrowRight':
                        nextSlide();
                        break;
                }}
            }}
        }});

        // Preload next/prev images for smooth navigation
        function preloadImages() {{
            slidesData.forEach((slide, index) => {{
                if (index < 10) {{ // Preload first 10 images
                    const img = new Image();
                    img.src = slide.image;
                }}
            }});
        }}

        // Initialize
        preloadImages();
    </script>
</body>
</html>"""

        # Write HTML file
        html_path = self.output_dir / "index.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\nHTML viewer generated: {html_path}")
        print(f"Total slides processed: {len(self.slides_data)}")

        if self.single_file:
            file_size = html_path.stat().st_size / (1024 * 1024)
            print(f"Single file size: {file_size:.1f}MB")
            print(f"Self-contained HTML file ready for sharing!")
        else:
            print(f"Multi-file viewer with separate image assets")

        print(f"Open {html_path} in your browser to view slides")

def main():
    parser = argparse.ArgumentParser(description='Convert PDFs to a browsable slide viewer')
    parser.add_argument('pdfs', nargs='+', help='PDF files or directory containing PDFs')
    parser.add_argument('--output', '-o', default='slide_viewer', help='Output directory (default: slide_viewer)')
    parser.add_argument('--thumbnail-size', default='300x200', help='Thumbnail size as WIDTHxHEIGHT (default: 300x200)')
    parser.add_argument('--quality', type=int, default=85, help='Image quality 1-100 (default: 85)')
    parser.add_argument('--single-file', action='store_true', help='Create a single HTML file with embedded images (larger file, easier to share)')

    args = parser.parse_args()

    # Parse thumbnail size
    try:
        width, height = map(int, args.thumbnail_size.split('x'))
        thumbnail_size = (width, height)
    except ValueError:
        print("Error: thumbnail-size must be in format WIDTHxHEIGHT (e.g., 300x200)")
        sys.exit(1)

    # Collect PDF files
    pdf_files = []
    for path_arg in args.pdfs:
        path = Path(path_arg)
        if path.is_file() and path.suffix.lower() == '.pdf':
            pdf_files.append(path)
        elif path.is_dir():
            pdf_files.extend(path.glob('*.pdf'))
            pdf_files.extend(path.glob('*.PDF'))
        else:
            print(f"Warning: {path} is not a valid PDF file or directory")

    if not pdf_files:
        print("No PDF files found!")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF files")

    # Create viewer
    viewer = PDFSlideViewer(
        output_dir=args.output,
        thumbnail_size=thumbnail_size,
        quality=args.quality,
        single_file=args.single_file
    )

    # Process PDFs
    viewer.process_pdfs(pdf_files)

    # Generate HTML viewer
    if viewer.slides_data:
        viewer.generate_html_viewer()
    else:
        print("No slides were processed successfully!")

if __name__ == "__main__":
    main()



